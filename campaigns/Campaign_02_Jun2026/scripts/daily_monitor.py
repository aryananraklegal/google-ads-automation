"""
daily_monitor.py
Usage: python daily_monitor.py [YYYY-MM-DD] [YYYY-MM-DD]
Default: yesterday only.
Output: ../review/YYYY-MM-DD_daily.md
Read-only. Makes zero API write calls.
"""
import sys
import os
from datetime import date, timedelta
from google.ads.googleads.client import GoogleAdsClient

SECRETS = os.path.join(os.path.dirname(__file__), "..", "secrets", "google-ads.yaml")
REVIEW  = os.path.join(os.path.dirname(__file__), "..", "review")
CID     = "2183727993"

CAMPAIGNS = {
    "23976339058": "Students",
    "23966712858": "Lawyers",
}

THRESHOLDS = {
    "Students": {"min_ctr": 0.04, "max_cpa": 300, "min_budget_util": 0.70, "daily_budget": 700, "launch_date": "2026-06-25"},
    "Lawyers":  {"min_ctr": 0.02, "max_cpa": 900, "min_budget_util": 0.70, "daily_budget": 300, "launch_date": "2026-06-25"},
}
LEARNING_PHASE_DAYS = 14  # suppress budget-util flag during PMax learning phase

def load_client():
    import yaml
    with open(SECRETS, "r") as f:
        cfg = yaml.safe_load(f)
    cfg["login_customer_id"] = "2183727993"
    return GoogleAdsClient.load_from_dict(cfg)

def date_range(args):
    if len(args) >= 3:
        return args[1], args[2]
    yesterday = date.today() - timedelta(days=1)
    return str(yesterday), str(yesterday)

def query_campaigns(ga, start, end):
    q = f"""
    SELECT campaign.id, campaign.name, campaign.status,
      metrics.cost_micros, metrics.clicks, metrics.impressions,
      metrics.conversions, metrics.ctr, metrics.average_cpc
    FROM campaign
    WHERE segments.date BETWEEN '{start}' AND '{end}'
    ORDER BY metrics.cost_micros DESC
    """
    return list(ga.search(customer_id=CID, query=q))

def query_devices(ga, start, end):
    q = f"""
    SELECT campaign.name, segments.device,
      metrics.clicks, metrics.impressions, metrics.cost_micros
    FROM campaign
    WHERE segments.date BETWEEN '{start}' AND '{end}'
    ORDER BY metrics.clicks DESC
    """
    return list(ga.search(customer_id=CID, query=q))

def query_landing(ga, start, end):
    q = f"""
    SELECT landing_page_view.unexpanded_final_url,
      metrics.clicks, metrics.cost_micros, metrics.conversions
    FROM landing_page_view
    WHERE segments.date BETWEEN '{start}' AND '{end}'
    ORDER BY metrics.clicks DESC
    LIMIT 10
    """
    return list(ga.search(customer_id=CID, query=q))

def flag(condition, msg, severity="⚠️"):
    return f"{severity} **FLAG:** {msg}" if condition else None

def build_report(start, end, campaigns, devices, landing):
    flags = []
    lines = []

    lines.append(f"# Daily Monitor — {start} to {end}\n")
    lines.append(f"Account: `customers/{CID}`\n")

    # Campaign summary
    lines.append("## Campaign Summary\n")
    lines.append("| Campaign | Status | Clicks | Impr | CTR | Avg CPC | Spend | Conv |")
    lines.append("|---|---|---|---|---|---|---|---|")

    for row in campaigns:
        c, m = row.campaign, row.metrics
        name = c.name
        status = c.status.name
        spend = m.cost_micros / 1e6
        ctr = m.ctr
        cpc = m.average_cpc / 1e6
        label = CAMPAIGNS.get(str(c.id), name)
        lines.append(f"| {name} | {status} | {m.clicks} | {m.impressions} | {ctr:.2%} | ₹{cpc:.2f} | ₹{spend:.2f} | {m.conversions:.0f} |")

        t = THRESHOLDS.get(label, {})
        if t:
            days = (date.fromisoformat(end) - date.fromisoformat(start)).days + 1
            expected_spend = t["daily_budget"] * days
            util = spend / expected_spend if expected_spend > 0 else 0
            flags.append(flag(ctr < t["min_ctr"] and m.impressions > 100, f"{name}: CTR {ctr:.2%} below threshold {t['min_ctr']:.0%}"))
            launch = date.fromisoformat(t.get("launch_date", start))
            days_live = (date.fromisoformat(end) - launch).days + 1
            in_learning = days_live <= LEARNING_PHASE_DAYS
            flags.append(flag(not in_learning and util < t["min_budget_util"] and m.clicks > 0, f"{name}: Budget utilisation {util:.0%} below 70% (spent ₹{spend:.0f} of ₹{expected_spend:.0f})"))
            flags.append(flag(m.conversions == 0 and m.clicks > 50, f"{name}: 0 conversions with {m.clicks} clicks — verify tracking", "🔴"))
            if m.conversions > 0:
                flags.append(flag((spend / m.conversions) > t["max_cpa"], f"{name}: CPA Rs{spend/m.conversions:.0f} exceeds threshold Rs{t['max_cpa']}"))

    # Device breakdown
    lines.append("\n## Device Breakdown\n")
    lines.append("| Campaign | Device | Clicks | Impr | Spend |")
    lines.append("|---|---|---|---|---|")
    for row in devices:
        m = row.metrics
        if m.clicks > 0:
            lines.append(f"| {row.campaign.name} | {row.segments.device.name} | {m.clicks} | {m.impressions} | ₹{m.cost_micros/1e6:.2f} |")

    # Landing pages
    lines.append("\n## Landing Pages\n")
    lines.append("| URL | Clicks | Spend | Conv |")
    lines.append("|---|---|---|---|")
    for row in landing:
        m = row.metrics
        if m.clicks > 0:
            lines.append(f"| {row.landing_page_view.unexpanded_final_url} | {m.clicks} | ₹{m.cost_micros/1e6:.2f} | {m.conversions:.0f} |")

    # Flags
    active_flags = [f for f in flags if f]
    lines.append("\n## Flags\n")
    if active_flags:
        for f in active_flags:
            lines.append(f)
            lines.append("")
    else:
        lines.append("✅ No threshold breaches detected.")

    lines.append(f"\n---\n*Generated: {date.today()} | Read-only run — no changes made.*")
    return "\n".join(lines)

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    start, end = date_range(sys.argv)
    client = load_client()
    ga = client.get_service("GoogleAdsService")

    print(f"Pulling data {start} → {end} ...")
    campaigns = query_campaigns(ga, start, end)
    devices   = query_devices(ga, start, end)
    landing   = query_landing(ga, start, end)

    report = build_report(start, end, campaigns, devices, landing)

    os.makedirs(REVIEW, exist_ok=True)
    out = os.path.join(REVIEW, f"{end}_daily.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\nSaved → {out}")

if __name__ == "__main__":
    main()
