"""
creative_report.py
Usage: python creative_report.py [YYYY-MM-DD] [YYYY-MM-DD]
Default: last 7 days.
Output: ../review/YYYY-MM-DD_creatives.md
Read-only. Makes zero API write calls.
"""
import sys
import os
from datetime import date, timedelta
from google.ads.googleads.client import GoogleAdsClient

SECRETS = os.path.join(os.path.dirname(__file__), "..", "secrets", "google-ads.yaml")
REVIEW  = os.path.join(os.path.dirname(__file__), "..", "review")
CID     = "2183727993"

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

def query_assets(ga, start, end):
    # performance_label is not queryable via GAQL in v24 — omit it
    q = f"""
    SELECT asset.name, asset.type, asset.text_asset.text,
      asset_group_asset.field_type,
      asset_group.name, campaign.name,
      metrics.impressions, metrics.clicks, metrics.cost_micros
    FROM asset_group_asset
    WHERE segments.date BETWEEN '{start}' AND '{end}'
      AND campaign.advertising_channel_type = PERFORMANCE_MAX
    ORDER BY metrics.impressions DESC
    """
    return list(ga.search(customer_id=CID, query=q))

def build_report(start, end, rows):
    lines = []
    lines.append(f"# Creative Performance — {start} to {end}\n")
    lines.append(f"Account: `customers/{CID}`\n")

    low_assets = []
    best_assets = []

    lines.append("## All Assets\n")
    lines.append("| Asset | Type | Field | Campaign | Impr | Clicks | Spend |")
    lines.append("|---|---|---|---|---|---|---|")

    for row in rows:
        a    = row.asset
        aga  = row.asset_group_asset
        m    = row.metrics
        text  = a.text_asset.text if a.type_.name == "TEXT" else f"[{a.type_.name}]"
        name  = (text[:40] + "...") if len(text) > 40 else text
        spend = m.cost_micros / 1e6

        lines.append(f"| {name} | {a.type_.name} | {aga.field_type.name} | {row.campaign.name[:20]} | {m.impressions} | {m.clicks} | Rs{spend:.2f} |")

    lines.append("\n## Note\n")
    lines.append("Performance labels (Best/Good/Low) are only shown in the Google Ads UI — not queryable via API.")
    lines.append("Check the Asset Group editor manually for label status. Flag any 'Low' assets here for replacement.")

    lines.append(f"\n---\n*Generated: {date.today()} | Read-only — no changes made.*")
    return "\n".join(lines)

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    start, end = date_range(sys.argv)
    client = load_client()
    ga = client.get_service("GoogleAdsService")

    print(f"Pulling creative performance {start} → {end} ...")
    rows = query_assets(ga, start, end)

    report = build_report(start, end, rows)

    os.makedirs(REVIEW, exist_ok=True)
    out = os.path.join(REVIEW, f"{end}_creatives.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\nSaved → {out}")

if __name__ == "__main__":
    main()
