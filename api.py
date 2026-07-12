"""
api.py — Addy's read-only Google Ads API connector.

Universal: works on any OS, any machine, any account.
Configure once in config.yaml. Credentials in secrets/google-ads.yaml.
No logic. No write operations. Returns structured data + saves to review/.
"""

import sys
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
SECRETS_PATH = ROOT / "secrets" / "google-ads.yaml"
OUTPUT_DIR = ROOT / "review"
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def _load_config() -> dict:
    import yaml
    config_path = ROOT / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(
            "config.yaml not found. Copy config.yaml.example and fill in your account details."
        )
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _customer_id() -> str:
    return _load_config()["account"]["customer_id"]


# ---------------------------------------------------------------------------
# Client + error handling
# ---------------------------------------------------------------------------

def _get_client():
    from google.ads.googleads.client import GoogleAdsClient
    if not SECRETS_PATH.exists():
        raise FileNotFoundError(
            f"Credentials not found at {SECRETS_PATH}\n"
            "Place your google-ads.yaml in the secrets/ folder."
        )
    client = GoogleAdsClient.load_from_storage(str(SECRETS_PATH))
    customer_id = _customer_id()
    client.login_customer_id = customer_id
    return client, customer_id


def _run_query(client, customer_id: str, query: str) -> list:
    from google.ads.googleads.errors import GoogleAdsException
    try:
        ga_svc = client.get_service("GoogleAdsService")
        response = ga_svc.search(customer_id=customer_id, query=query)
        return list(response)
    except GoogleAdsException as ex:
        errors = [e.message for e in ex.failure.errors]
        raise RuntimeError(f"Google Ads API error: {errors}") from ex
    except Exception as ex:
        raise RuntimeError(f"Unexpected error querying Google Ads: {ex}") from ex


def _validate_dates(start_date: str, end_date: str):
    try:
        s = datetime.strptime(start_date, "%Y-%m-%d")
        e = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Dates must be YYYY-MM-DD format. Got: {start_date}, {end_date}")
    if s > e:
        raise ValueError(f"start_date {start_date} is after end_date {end_date}")


def _save(filename: str, content: str) -> Path:
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    print(f"Saved -> {path}")
    return path


def _default_dates(start_date, end_date):
    if not end_date:
        end_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    if not start_date:
        start_date = end_date
    return start_date, end_date


# ---------------------------------------------------------------------------
# 1. CAMPAIGN METRICS
# ---------------------------------------------------------------------------

def get_metrics(start_date: str = None, end_date: str = None) -> dict:
    """Fetch clicks, impressions, cost, conversions for all campaigns."""
    start_date, end_date = _default_dates(start_date, end_date)
    _validate_dates(start_date, end_date)

    client, customer_id = _get_client()
    query = f"""
        SELECT
            campaign.name,
            campaign.status,
            campaign.id,
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_per_conversion,
            metrics.conversions_from_interactions_rate
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """

    rows = _run_query(client, customer_id, query)

    lines = [f"# Campaign Metrics: {start_date} to {end_date}\n"]
    results = []

    for row in rows:
        m = row.metrics
        c = row.campaign
        cost_inr = round(m.cost_micros / 1_000_000, 2)
        cpc_inr = round(m.average_cpc / 1_000_000, 2)
        # cost_per_conversion is Google's own CPA. It is 0 when conversions are 0,
        # which would read as "free" rather than "no data" — surface None instead.
        cpa_inr = round(m.cost_per_conversion / 1_000_000, 2) if m.conversions else None

        entry = {
            "campaign": c.name,
            "status": c.status.name,
            "clicks": m.clicks,
            "impressions": m.impressions,
            "cost_inr": cost_inr,
            "conversions": m.conversions,
            "ctr_pct": round(m.ctr * 100, 2),
            "avg_cpc_inr": cpc_inr,
            "cpa_inr": cpa_inr,
            "cvr_pct": round(m.conversions_from_interactions_rate * 100, 2),
        }
        results.append(entry)
        lines.append(f"## {c.name} ({c.status.name})")
        lines.append(f"- Clicks: {m.clicks} | Impressions: {m.impressions} | CTR: {entry['ctr_pct']}%")
        lines.append(f"- Spend: {cost_inr} | Avg CPC: {cpc_inr}")
        lines.append(f"- Conversions: {m.conversions} | CVR: {entry['cvr_pct']}%")
        lines.append(f"- CPA: {cpa_inr if cpa_inr is not None else 'no conversions'}\n")

    _save(f"{end_date}_metrics.md", "\n".join(lines))
    return {"date_range": f"{start_date} to {end_date}", "campaigns": results}


# ---------------------------------------------------------------------------
# 2. SEARCH TERMS
# ---------------------------------------------------------------------------

def get_search_terms(start_date: str = None, end_date: str = None) -> dict:
    """Fetch search terms report."""
    start_date, end_date = _default_dates(start_date, end_date)
    _validate_dates(start_date, end_date)

    client, customer_id = _get_client()
    query = f"""
        SELECT
            search_term_view.search_term,
            campaign.name,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.cost_micros
        FROM search_term_view
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY metrics.clicks DESC
        LIMIT 100
    """

    rows = _run_query(client, customer_id, query)

    lines = [f"# Search Terms: {start_date} to {end_date}\n"]
    results = []

    for row in rows:
        m = row.metrics
        cost_inr = round(m.cost_micros / 1_000_000, 2)
        entry = {
            "term": row.search_term_view.search_term,
            "campaign": row.campaign.name,
            "clicks": m.clicks,
            "impressions": m.impressions,
            "conversions": m.conversions,
            "cost_inr": cost_inr,
        }
        results.append(entry)
        lines.append(
            f"- `{entry['term']}` | {entry['campaign']} | "
            f"{entry['clicks']} clicks | {cost_inr}"
        )

    _save(f"{end_date}_search_terms.md", "\n".join(lines))
    return {"date_range": f"{start_date} to {end_date}", "terms": results}


# ---------------------------------------------------------------------------
# 3. ASSET / CREATIVE PERFORMANCE
# ---------------------------------------------------------------------------

# Minimum impressions before an asset is judged on conversions rather than left
# in LEARNING. This account converts at roughly 0.2% of impressions, so an asset
# needs several hundred impressions before "zero conversions" means anything.
# Set too low, every under-served asset is labelled LOW and looks prunable.
CREATIVE_MIN_IMPRESSIONS = 500

CREATIVE_CAVEAT = (
    "PMax credits an asset for every conversion from any combination it appeared in. "
    "Asset conversions therefore OVERLAP and do NOT sum to the campaign total. "
    "Use them to rank assets against each other, never to attribute volume."
)


def _label_creatives(entries: list) -> None:
    """Assign a relative performance label in place, within each field type.

    Google removed asset_group_asset.performance_label in v24, so we derive the
    equivalent from live metrics. Assets are ranked against their own field type
    (a HEADLINE only competes with other HEADLINEs) by conversions, then by
    conversion rate. Terciles map to BEST / GOOD / LOW, mirroring Google's labels.
    """
    groups = defaultdict(list)
    for e in entries:
        groups[(e["campaign"], e["asset_group"], e["field_type"])].append(e)

    for members in groups.values():
        for e in members:
            e["cvr"] = (e["conversions"] / e["impressions"]) if e["impressions"] else 0.0

        judged = [e for e in members if e["impressions"] >= CREATIVE_MIN_IMPRESSIONS]
        for e in members:
            if e not in judged:
                e["performance_label"] = "LEARNING"

        if not judged:
            continue

        # An asset that has been served enough and still converts nobody is LOW,
        # regardless of where it ranks. The rest split BEST / GOOD by conversions.
        converters = [e for e in judged if e["conversions"] > 0]
        for e in judged:
            if e["conversions"] == 0:
                e["performance_label"] = "LOW"

        converters.sort(key=lambda e: (e["conversions"], e["cvr"]), reverse=True)
        cut = max(1, len(converters) // 3)
        for rank, e in enumerate(converters):
            e["performance_label"] = "BEST" if rank < cut else "GOOD"


def get_creatives(start_date: str = None, end_date: str = None) -> dict:
    """Fetch PMax asset group assets with derived performance labels.

    Replaces the v24-removed asset_group_asset.performance_label with labels
    derived from live per-asset metrics. See CREATIVE_CAVEAT on why the
    conversion column does not add up to the campaign total.
    """
    start_date, end_date = _default_dates(start_date, end_date)
    _validate_dates(start_date, end_date)

    client, customer_id = _get_client()
    query = f"""
        SELECT
            asset_group_asset.asset,
            asset_group_asset.field_type,
            asset_group_asset.status,
            asset_group_asset.primary_status,
            asset_group_asset.policy_summary.approval_status,
            asset_group.name,
            campaign.name,
            asset.type,
            asset.source,
            asset.text_asset.text,
            asset.youtube_video_asset.youtube_video_id,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros
        FROM asset_group_asset
        WHERE campaign.status != 'REMOVED'
        AND asset_group_asset.status != 'REMOVED'
        AND segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY asset_group.name
    """

    rows = _run_query(client, customer_id, query)

    results = []
    for row in rows:
        aga, asset, m = row.asset_group_asset, row.asset, row.metrics
        results.append({
            "campaign": row.campaign.name,
            "asset_group": row.asset_group.name,
            "field_type": aga.field_type.name,
            "asset_type": asset.type_.name,
            "auto_generated": asset.source.name == "AUTOMATICALLY_CREATED",
            "approval_status": aga.policy_summary.approval_status.name,
            "primary_status": aga.primary_status.name,
            "content": (
                asset.text_asset.text
                or asset.youtube_video_asset.youtube_video_id
                or ""
            ),
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": m.conversions,
            "cost_inr": round(m.cost_micros / 1_000_000, 2),
            "asset": aga.asset,
        })

    _label_creatives(results)

    disapproved = [e for e in results if e["approval_status"] not in ("APPROVED", "UNSPECIFIED", "UNKNOWN")]
    auto_gen = [e for e in results if e["auto_generated"]]
    low = [e for e in results if e["performance_label"] == "LOW"]

    order = {"BEST": 0, "GOOD": 1, "LOW": 2, "LEARNING": 3}
    results.sort(key=lambda e: (e["asset_group"], e["field_type"], order[e["performance_label"]]))

    lines = [
        f"# Creative Performance: {start_date} to {end_date}\n",
        f"> NOTE: {CREATIVE_CAVEAT}\n",
        f"Assets: {len(results)} | LOW: {len(low)} | "
        f"auto-generated: {len(auto_gen)} | disapproved: {len(disapproved)}\n",
    ]
    for e in results:
        flags = ""
        if e["auto_generated"]:
            flags += " [AUTO-GEN]"
        if e in disapproved:
            flags += f" [{e['approval_status']}]"
        lines.append(
            f"- [{e['performance_label']}] {e['field_type']} | "
            f"imp={e['impressions']} clk={e['clicks']} conv={e['conversions']:.0f} "
            f"cost=INR{e['cost_inr']}{flags}\n"
            f"    {e['content'][:70]}"
        )

    _save(f"{end_date}_creatives.md", "\n".join(lines))
    return {
        "date_range": f"{start_date} to {end_date}",
        "caveat": CREATIVE_CAVEAT,
        "counts": {
            "total": len(results),
            "low": len(low),
            "auto_generated": len(auto_gen),
            "disapproved": len(disapproved),
        },
        "assets": results,
    }


# ---------------------------------------------------------------------------
# 4. CAMPAIGN LIST
# ---------------------------------------------------------------------------

def get_campaigns() -> dict:
    """Fetch all campaigns with status and daily budget."""
    client, customer_id = _get_client()
    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign_budget.amount_micros,
            campaign_budget.resource_name
        FROM campaign
        WHERE campaign.status != 'REMOVED'
        ORDER BY campaign.name
    """

    rows = _run_query(client, customer_id, query)

    lines = ["# Campaigns\n"]
    results = []

    for row in rows:
        c = row.campaign
        budget_inr = round(row.campaign_budget.amount_micros / 1_000_000, 2)
        entry = {
            "id": c.id,
            "name": c.name,
            "status": c.status.name,
            "type": c.advertising_channel_type.name,
            "daily_budget_inr": budget_inr,
            "budget_resource": row.campaign_budget.resource_name,
        }
        results.append(entry)
        lines.append(
            f"- [{entry['status']}] {entry['name']} (ID: {entry['id']}) | "
            f"{budget_inr}/day | {entry['type']}"
        )

    _save("campaigns.md", "\n".join(lines))
    return {"campaigns": results}


# ---------------------------------------------------------------------------
# 5. CONVERSION ACTIONS
# ---------------------------------------------------------------------------

def get_conversion_actions() -> dict:
    """Fetch all conversion actions and their status. Use to verify tracking is live."""
    client, customer_id = _get_client()
    query = """
        SELECT
            conversion_action.id,
            conversion_action.name,
            conversion_action.status,
            conversion_action.type,
            conversion_action.counting_type
        FROM conversion_action
        WHERE conversion_action.status != 'REMOVED'
    """

    rows = _run_query(client, customer_id, query)

    lines = ["# Conversion Actions\n"]
    results = []

    for row in rows:
        ca = row.conversion_action
        entry = {
            "id": ca.id,
            "name": ca.name,
            "status": ca.status.name,
            "type": ca.type_.name,
            "counting": ca.counting_type.name,
        }
        results.append(entry)
        lines.append(
            f"- [{entry['status']}] {entry['name']} (ID: {entry['id']}) | "
            f"Count: {entry['counting']}"
        )

    _save("conversion_actions.md", "\n".join(lines))
    return {"conversion_actions": results}


# ---------------------------------------------------------------------------
# 6. BIDDING PHASE STATUS
# ---------------------------------------------------------------------------

def get_bidding_phase_status(window_days: int = 30) -> dict:
    """
    Returns current conversion count within rolling window.
    Used by council to determine if bid strategy graduation is safe.
    """
    end_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    start_date = (datetime.today() - timedelta(days=window_days)).strftime("%Y-%m-%d")

    client, customer_id = _get_client()
    query = f"""
        SELECT
            campaign.name,
            campaign.id,
            metrics.conversions
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status != 'REMOVED'
    """

    rows = _run_query(client, customer_id, query)
    config = _load_config()
    thresholds = config.get("thresholds", {}).get("bidding_phase", {})

    results = []
    for row in rows:
        conv = row.metrics.conversions
        phase = "COLD_START"
        if conv >= thresholds.get("optimize_min_conversions", 30):
            phase = "OPTIMIZATION"
        elif conv >= thresholds.get("growth_min_conversions", 15):
            phase = "GROWTH"

        results.append({
            "campaign": row.campaign.name,
            "conversions_in_window": conv,
            "window_days": window_days,
            "window_start": start_date,
            "current_phase": phase,
            "next_phase_requires": (
                f"{thresholds.get('growth_min_conversions', 15)} conv in {window_days}d"
                if phase == "COLD_START"
                else f"{thresholds.get('optimize_min_conversions', 30)} conv in {window_days}d"
                if phase == "GROWTH"
                else "Already at max phase"
            ),
        })

    lines = [f"# Bidding Phase Status (rolling {window_days} days)\n"]
    for r in results:
        lines.append(f"## {r['campaign']}")
        lines.append(f"- Phase: {r['current_phase']}")
        lines.append(f"- Conversions in window: {r['conversions_in_window']}")
        lines.append(f"- Next phase: {r['next_phase_requires']}\n")

    _save("bidding_phase.md", "\n".join(lines))
    return {"window_days": window_days, "campaigns": results}


# ---------------------------------------------------------------------------
# 7. PMAX SEARCH TERM INSIGHTS
# ---------------------------------------------------------------------------

# PMax traffic never lands in search_term_view (that resource is Search-network
# only). Google's PMax equivalent is campaign_search_term_insight, which buckets
# queries into categories for privacy — raw search terms are only exposed within
# a category, and only once that category has enough volume. Treat this as
# directional theme signal, not the literal query list Search campaigns get.
PMAX_SEARCH_TERM_CAVEAT = (
    "PMax does not report into search_term_view. campaign_search_term_insight "
    "buckets queries into categories for privacy — individual search terms are "
    "only visible within a category, and only once that category has enough "
    "volume. This is directional theme signal, not a literal query list."
)

# campaign_search_term_insight requires REQUIRES_FILTER_BY_SINGLE_RESOURCE, and
# fetching the terms under a category costs one extra API call per category —
# cap how many categories get the term-level lookup so this stays a handful of
# calls, not one per category on a large account.
PMAX_CATEGORY_TERM_FETCH_LIMIT = 20


def _resolve_single_enabled_pmax_campaign(client, customer_id: str) -> int:
    query = """
        SELECT campaign.id, campaign.name
        FROM campaign
        WHERE campaign.status = 'ENABLED'
        AND campaign.advertising_channel_type = 'PERFORMANCE_MAX'
    """
    rows = _run_query(client, customer_id, query)
    matches = [(r.campaign.id, r.campaign.name) for r in rows]
    if len(matches) == 0:
        raise ValueError("No ENABLED PMax campaign found — pass campaign_id explicitly.")
    if len(matches) > 1:
        names = ", ".join(f"{n} ({i})" for i, n in matches)
        raise ValueError(f"Multiple ENABLED PMax campaigns found ({names}) — pass campaign_id explicitly.")
    return matches[0][0]


def get_pmax_search_terms(campaign_id: int = None, start_date: str = None, end_date: str = None) -> dict:
    """Fetch Performance Max search-term category insights.

    Two-step GAQL: campaign_search_term_insight must be filtered to exactly one
    campaign_id (REQUIRES_FILTER_BY_SINGLE_RESOURCE), and the underlying search
    terms per category require a second query filtered by that category's
    insight id. If campaign_id is omitted, auto-resolves to the single ENABLED
    PMax campaign; raises if there's zero or more than one.
    """
    start_date, end_date = _default_dates(start_date, end_date)
    _validate_dates(start_date, end_date)

    client, customer_id = _get_client()

    if campaign_id is None:
        campaign_id = _resolve_single_enabled_pmax_campaign(client, customer_id)

    category_query = f"""
        SELECT
            campaign_search_term_insight.campaign_id,
            campaign_search_term_insight.category_label,
            campaign_search_term_insight.id,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign_search_term_insight
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign_search_term_insight.campaign_id = {campaign_id}
        ORDER BY metrics.clicks DESC
    """
    category_rows = _run_query(client, customer_id, category_query)

    categories = []
    for row in category_rows:
        csi, m = row.campaign_search_term_insight, row.metrics
        categories.append({
            "insight_id": csi.id,
            "category_label": csi.category_label or "(uncategorized)",
            "clicks": m.clicks,
            "impressions": m.impressions,
            "conversions": m.conversions,
            "conversions_value": m.conversions_value,
        })

    top_categories = categories[:PMAX_CATEGORY_TERM_FETCH_LIMIT]
    dropped = len(categories) - len(top_categories)

    for cat in top_categories:
        term_query = f"""
            SELECT
                segments.search_term,
                segments.search_subcategory,
                metrics.impressions,
                metrics.conversions,
                metrics.conversions_value
            FROM campaign_search_term_insight
            WHERE campaign_search_term_insight.campaign_id = {campaign_id}
            AND campaign_search_term_insight.id = {cat['insight_id']}
            AND segments.date BETWEEN '{start_date}' AND '{end_date}'
        """
        # Google rejects ORDER BY when segmenting by segments.search_term — sort client-side instead.
        term_rows = _run_query(client, customer_id, term_query)
        cat["terms"] = sorted(
            (
                {
                    "term": r.segments.search_term,
                    "impressions": r.metrics.impressions,
                    "conversions": r.metrics.conversions,
                }
                for r in term_rows
            ),
            key=lambda t: t["impressions"],
            reverse=True,
        )

    lines = [
        f"# PMax Search Term Insights: {start_date} to {end_date} (campaign {campaign_id})\n",
        f"> NOTE: {PMAX_SEARCH_TERM_CAVEAT}\n",
    ]
    if dropped > 0:
        lines.append(
            f"> {dropped} lower-traffic categories omitted from term-level lookup "
            f"(top {PMAX_CATEGORY_TERM_FETCH_LIMIT} by clicks shown).\n"
        )
    for cat in top_categories:
        lines.append(
            f"## {cat['category_label']} — {cat['clicks']} clicks | "
            f"{cat['conversions']:.0f} conv"
        )
        for t in cat["terms"][:10]:
            lines.append(f"- `{t['term']}` | {t['impressions']} impr | {t['conversions']:.0f} conv")
        lines.append("")

    _save(f"{end_date}_pmax_search_terms.md", "\n".join(lines))
    return {
        "date_range": f"{start_date} to {end_date}",
        "campaign_id": campaign_id,
        "caveat": PMAX_SEARCH_TERM_CAVEAT,
        "categories_total": len(categories),
        "categories_fetched": len(top_categories),
        "categories": top_categories,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    start = sys.argv[2] if len(sys.argv) > 2 else None
    end = sys.argv[3] if len(sys.argv) > 3 else None

    commands = {
        "metrics": lambda: get_metrics(start, end),
        "search_terms": lambda: get_search_terms(start, end),
        "pmax_search_terms": lambda: get_pmax_search_terms(start_date=start, end_date=end),
        "creatives": lambda: get_creatives(start, end),
        "campaigns": lambda: get_campaigns(),
        "conversions": lambda: get_conversion_actions(),
        "bidding_phase": lambda: get_bidding_phase_status(),
    }

    if cmd not in commands:
        print(f"Usage: python api.py [{' | '.join(commands)}] [start_date] [end_date]")
        print("Dates format: YYYY-MM-DD. Defaults to yesterday if omitted.")
        sys.exit(1)

    try:
        result = commands[cmd]()
        print(json.dumps(result, indent=2, default=str))
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)
