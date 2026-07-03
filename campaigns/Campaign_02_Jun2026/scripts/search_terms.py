"""
search_terms.py
Usage: python search_terms.py [YYYY-MM-DD] [YYYY-MM-DD]
Default: last 7 days.
Output: ../review/YYYY-MM-DD_search_terms.md
Read-only. Makes zero API write calls.

Note: PMax campaigns do not expose individual search terms via the API.
This script uses campaign_search_term_insight (category-level aggregates)
for PMax, which is the correct API endpoint. Per-term data is not available.
"""
import sys
import os
from datetime import date, timedelta
from google.ads.googleads.client import GoogleAdsClient

SECRETS = os.path.join(os.path.dirname(__file__), "..", "secrets", "google-ads.yaml")
REVIEW  = os.path.join(os.path.dirname(__file__), "..", "review")
CID     = "2183727993"
WASTED_SPEND_THRESHOLD = 50  # INR — only applies to Search campaigns

def load_client():
    import yaml
    with open(SECRETS, "r") as f:
        cfg = yaml.safe_load(f)
    cfg["login_customer_id"] = "2183727993"
    return GoogleAdsClient.load_from_dict(cfg)

def date_range(args):
    if len(args) >= 3:
        return args[1], args[2]
    end   = date.today() - timedelta(days=1)
    start = end - timedelta(days=6)
    return str(start), str(end)

def query_pmax_insights(ga, start, end):
    """Category-level search term insights for PMax campaigns."""
    q = f"""
    SELECT campaign_search_term_insight.category_label,
      campaign.name,
      metrics.clicks, metrics.impressions, metrics.cost_micros, metrics.conversions
    FROM campaign_search_term_insight
    WHERE segments.date BETWEEN '{start}' AND '{end}'
    ORDER BY metrics.cost_micros DESC
    LIMIT 100
    """
    try:
        return list(ga.search(customer_id=CID, query=q)), "pmax"
    except Exception as e:
        return [], "pmax_error"

def query_search_terms(ga, start, end):
    """Per-term data for standard Search campaigns (not PMax)."""
    q = f"""
    SELECT search_term_view.search_term, campaign.name,
      metrics.clicks, metrics.impressions, metrics.cost_micros,
      metrics.conversions, metrics.ctr
    FROM search_term_view
    WHERE segments.date BETWEEN '{start}' AND '{end}'
    ORDER BY metrics.cost_micros DESC
    LIMIT 100
    """
    try:
        return list(ga.search(customer_id=CID, query=q))
    except Exception:
        return []

def build_report(start, end, pmax_rows, search_rows):
    lines = []
    lines.append(f"# Search Term Insights — {start} to {end}\n")
    lines.append(f"Account: `customers/{CID}`\n")

    # PMax category insights
    lines.append("## PMax Search Categories\n")
    lines.append("_Category-level only. Individual search terms are not available via API for PMax campaigns._\n")
    if pmax_rows:
        lines.append("| Category | Campaign | Clicks | Impr | Spend (₹) | Conv |")
        lines.append("|---|---|---|---|---|---|")
        for row in pmax_rows:
            m = row.metrics
            label = row.campaign_search_term_insight.category_label or "(unlabelled)"
            spend = m.cost_micros / 1e6
            lines.append(f"| {label} | {row.campaign.name} | {m.clicks} | {m.impressions} | ₹{spend:.2f} | {m.conversions:.0f} |")
    else:
        lines.append("No PMax search category data for this period.")
        lines.append("This is expected when campaigns are PAUSED or have <100 impressions.\n")

    # Standard Search terms (if any non-PMax campaigns exist)
    lines.append("\n## Standard Search Campaign Terms\n")
    if search_rows:
        lines.append("| Term | Campaign | Clicks | Impr | CTR | Spend (₹) | Conv |")
        lines.append("|---|---|---|---|---|---|---|")
        for row in search_rows:
            m = row.metrics
            spend = m.cost_micros / 1e6
            lines.append(f"| {row.search_term_view.search_term} | {row.campaign.name} | {m.clicks} | {m.impressions} | {m.ctr:.2%} | ₹{spend:.2f} | {m.conversions:.0f} |")

        # Wasted spend (only meaningful for standard Search)
        wasted = [r for r in search_rows if r.metrics.conversions == 0 and r.metrics.cost_micros / 1e6 >= WASTED_SPEND_THRESHOLD]
        if wasted:
            lines.append(f"\n### Wasted Spend Candidates (0 conv, spend ≥ ₹{WASTED_SPEND_THRESHOLD})\n")
            lines.append("**Do not add negatives yet — review with Kapil first.**\n")
            lines.append("| Term | Campaign | Spend (₹) | Clicks |")
            lines.append("|---|---|---|---|")
            for row in wasted:
                m = row.metrics
                lines.append(f"| {row.search_term_view.search_term} | {row.campaign.name} | ₹{m.cost_micros/1e6:.2f} | {m.clicks} |")
    else:
        lines.append("No standard Search campaign data (all campaigns are PMax).")

    lines.append(f"\n---\n*Generated: {date.today()} | Read-only — no changes made.*")
    return "\n".join(lines)

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    start, end = date_range(sys.argv)
    client = load_client()
    ga = client.get_service("GoogleAdsService")

    print(f"Pulling search term data {start} → {end} ...")
    pmax_rows, _ = query_pmax_insights(ga, start, end)
    search_rows   = query_search_terms(ga, start, end)

    report = build_report(start, end, pmax_rows, search_rows)

    os.makedirs(REVIEW, exist_ok=True)
    out = os.path.join(REVIEW, f"{end}_search_terms.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\nSaved → {out}")

if __name__ == "__main__":
    main()
