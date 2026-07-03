"""
api.py — Addy's read-only Google Ads API connector.

Universal: works on any OS, any machine, any account.
Configure once in config.yaml. Credentials in secrets/google-ads.yaml.
No logic. No write operations. Returns structured data + saves to review/.
"""

import sys
import json
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
            metrics.average_cpc
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

        entry = {
            "campaign": c.name,
            "status": c.status.name,
            "clicks": m.clicks,
            "impressions": m.impressions,
            "cost_inr": cost_inr,
            "conversions": m.conversions,
            "ctr_pct": round(m.ctr * 100, 2),
            "avg_cpc_inr": cpc_inr,
        }
        results.append(entry)
        lines.append(f"## {c.name} ({c.status.name})")
        lines.append(f"- Clicks: {m.clicks} | Impressions: {m.impressions} | CTR: {entry['ctr_pct']}%")
        lines.append(f"- Spend: {cost_inr} | Avg CPC: {cpc_inr}")
        lines.append(f"- Conversions: {m.conversions}\n")

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

def get_creatives(start_date: str = None, end_date: str = None) -> dict:
    """Fetch asset group asset performance labels."""
    start_date, end_date = _default_dates(start_date, end_date)
    _validate_dates(start_date, end_date)

    client, customer_id = _get_client()
    query = f"""
        SELECT
            asset_group_asset.asset,
            asset_group_asset.field_type,
            asset_group_asset.performance_label,
            asset_group.name,
            campaign.name
        FROM asset_group_asset
        WHERE campaign.status != 'REMOVED'
        AND segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY asset_group.name
    """

    rows = _run_query(client, customer_id, query)

    lines = [f"# Creative Performance: {start_date} to {end_date}\n"]
    results = []

    for row in rows:
        aga = row.asset_group_asset
        entry = {
            "asset_group": row.asset_group.name,
            "campaign": row.campaign.name,
            "field_type": aga.field_type.name,
            "performance_label": aga.performance_label.name,
            "asset": aga.asset,
        }
        results.append(entry)
        lines.append(
            f"- [{entry['performance_label']}] {entry['field_type']} | {entry['asset_group']}"
        )

    _save(f"{end_date}_creatives.md", "\n".join(lines))
    return {"date_range": f"{start_date} to {end_date}", "assets": results}


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
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    start = sys.argv[2] if len(sys.argv) > 2 else None
    end = sys.argv[3] if len(sys.argv) > 3 else None

    commands = {
        "metrics": lambda: get_metrics(start, end),
        "search_terms": lambda: get_search_terms(start, end),
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
