"""
execute.py — Addy's write connector.

Universal: works on any OS, any machine, any account.
All account constants loaded from config.yaml. No hardcoded IDs.

RULES — these are not suggestions:
1. Every call requires a council confirmation code (ADY-YYYYMMDD-XXX matching TODAY's date)
2. Current state is read and logged BEFORE every mutation
3. Rollback log written BEFORE every mutation
4. All API calls are wrapped — no bare exceptions propagate
5. Idempotent — skips if already in target state
"""

import sys
import re
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
SECRETS_PATH = ROOT / "secrets" / "google-ads.yaml"
OUTPUT_DIR = ROOT / "review"
OUTPUT_DIR.mkdir(exist_ok=True)
TODAY = datetime.today().strftime("%Y-%m-%d")
SESSION_LOG = OUTPUT_DIR / f"{TODAY}_session.md"
ROLLBACK_LOG = OUTPUT_DIR / f"{TODAY}_rollback.md"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def _load_config() -> dict:
    import yaml
    config_path = ROOT / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found. See config.yaml.example.")
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _customer_id() -> str:
    return _load_config()["account"]["customer_id"]


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

def _get_client():
    from google.ads.googleads.client import GoogleAdsClient
    if not SECRETS_PATH.exists():
        raise FileNotFoundError(
            f"Credentials not found at {SECRETS_PATH}\n"
            "Place google-ads.yaml in the secrets/ folder."
        )
    customer_id = _customer_id()
    client = GoogleAdsClient.load_from_storage(str(SECRETS_PATH))
    client.login_customer_id = customer_id
    return client, customer_id


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _log(message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    with open(SESSION_LOG, "a", encoding="utf-8") as f:
        f.write(entry)
    print(entry.strip())


def _rollback_log(action: str, before_state: dict):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = (
        f"\n## [{timestamp}] BEFORE: {action}\n"
        f"```json\n{json.dumps(before_state, indent=2, default=str)}\n```\n"
    )
    with open(ROLLBACK_LOG, "a", encoding="utf-8") as f:
        f.write(entry)


# ---------------------------------------------------------------------------
# Confirmation code validation
# ---------------------------------------------------------------------------

def _validate_code(code: str, action_label: str = ""):
    """
    Validates council confirmation code.
    Format: ADY-YYYYMMDD-XXX
    - Date component must match today
    - Reuse within same session is prevented by session log check
    """
    if not isinstance(code, str):
        raise ValueError("Confirmation code must be a string.")

    pattern = r"^ADY-(\d{8})-([A-Z0-9]{3})$"
    match = re.match(pattern, code)
    if not match:
        raise ValueError(
            f"Invalid confirmation code: '{code}'\n"
            "Format required: ADY-YYYYMMDD-XXX (e.g. ADY-20260703-001)\n"
            "Run /ads-council to generate a valid code before executing."
        )

    code_date = match.group(1)
    today_compact = TODAY.replace("-", "")
    if code_date != today_compact:
        raise ValueError(
            f"Confirmation code date {code_date} does not match today {today_compact}.\n"
            "Council codes expire at midnight. Run /ads-council to get a fresh code."
        )

    # Replay prevention: check session log for prior use of this exact code
    if SESSION_LOG.exists():
        session_content = SESSION_LOG.read_text(encoding="utf-8")
        if f"code:{code}" in session_content:
            raise ValueError(
                f"Confirmation code {code} has already been used in this session.\n"
                "Each council code authorises one action. Run /ads-council for a new code."
            )

    _log(f"CODE VALIDATED: {code} | action: {action_label} | code:{code}")


# ---------------------------------------------------------------------------
# API call wrapper
# ---------------------------------------------------------------------------

def _mutate(operation_fn, label: str):
    """Wraps any Google Ads mutate call with full error handling."""
    from google.ads.googleads.errors import GoogleAdsException
    try:
        return operation_fn()
    except GoogleAdsException as ex:
        errors = [
            f"{e.error_code} — {e.message}"
            for e in ex.failure.errors
        ]
        _log(f"GOOGLE ADS API ERROR during {label}: {errors}")
        raise RuntimeError(f"Google Ads API error during {label}: {errors}") from ex
    except Exception as ex:
        _log(f"UNEXPECTED ERROR during {label}: {ex}")
        raise RuntimeError(f"Unexpected error during {label}: {ex}") from ex


def _query(client, customer_id: str, query: str, label: str) -> list:
    """Wraps any Google Ads search query with full error handling."""
    from google.ads.googleads.errors import GoogleAdsException
    try:
        ga_svc = client.get_service("GoogleAdsService")
        return list(ga_svc.search(customer_id=customer_id, query=query))
    except GoogleAdsException as ex:
        errors = [f"{e.error_code} — {e.message}" for e in ex.failure.errors]
        raise RuntimeError(f"Google Ads API error during {label}: {errors}") from ex
    except Exception as ex:
        raise RuntimeError(f"Unexpected error during {label}: {ex}") from ex


# ---------------------------------------------------------------------------
# Current state readers
# ---------------------------------------------------------------------------

def _get_campaign_current(client, customer_id: str, resource_name: str) -> dict:
    query = f"""
        SELECT campaign.status, campaign.name, campaign.id
        FROM campaign
        WHERE campaign.resource_name = '{resource_name}'
    """
    rows = _query(client, customer_id, query, "get_campaign_current")
    if not rows:
        raise ValueError(f"Campaign not found: {resource_name}")
    c = rows[0].campaign
    return {"resource_name": resource_name, "name": c.name, "id": c.id, "status": c.status.name}


def _get_budget_current(client, customer_id: str, budget_resource_name: str) -> dict:
    query = f"""
        SELECT campaign_budget.amount_micros, campaign_budget.name, campaign_budget.resource_name
        FROM campaign_budget
        WHERE campaign_budget.resource_name = '{budget_resource_name}'
    """
    rows = _query(client, customer_id, query, "get_budget_current")
    if not rows:
        raise ValueError(f"Budget not found: {budget_resource_name}")
    b = rows[0].campaign_budget
    return {
        "resource_name": b.resource_name,
        "name": b.name,
        "amount_micros": b.amount_micros,
        "amount_inr": round(b.amount_micros / 1_000_000, 2),
    }


def _get_bid_strategy_current(client, customer_id: str, campaign_resource_name: str) -> dict:
    """Reads the actual current bid strategy from the API before any mutation."""
    query = f"""
        SELECT
            campaign.bidding_strategy_type,
            campaign.target_cpa.target_cpa_micros,
            campaign.maximize_clicks.target_spend_micros,
            campaign.name
        FROM campaign
        WHERE campaign.resource_name = '{campaign_resource_name}'
    """
    rows = _query(client, customer_id, query, "get_bid_strategy_current")
    if not rows:
        raise ValueError(f"Campaign not found: {campaign_resource_name}")
    c = rows[0].campaign
    state = {
        "resource_name": campaign_resource_name,
        "name": c.name,
        "bidding_strategy_type": c.bidding_strategy_type.name,
    }
    if c.target_cpa.target_cpa_micros:
        state["target_cpa_inr"] = round(c.target_cpa.target_cpa_micros / 1_000_000, 2)
    return state


# ---------------------------------------------------------------------------
# 1. PAUSE CAMPAIGN
# ---------------------------------------------------------------------------

def pause_campaign(campaign_resource_name: str, confirmation_code: str) -> dict:
    """Pause a campaign. Skips if already paused."""
    _validate_code(confirmation_code, f"pause_campaign:{campaign_resource_name}")
    client, customer_id = _get_client()

    before = _get_campaign_current(client, customer_id, campaign_resource_name)
    _rollback_log("pause_campaign", before)

    if before["status"] == "PAUSED":
        _log(f"SKIP: {before['name']} already PAUSED")
        return {"skipped": True, "reason": "already_paused", "campaign": before["name"]}

    campaign_svc = client.get_service("CampaignService")
    campaign = client.get_type("Campaign")
    campaign.resource_name = campaign_resource_name
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    op = client.get_type("CampaignOperation")
    op.update.CopyFrom(campaign)
    op.update_mask.paths.append("status")

    _mutate(
        lambda: campaign_svc.mutate_campaigns(customer_id=customer_id, operations=[op]),
        f"pause_campaign:{before['name']}"
    )
    _log(f"PAUSED: {before['name']} | code:{confirmation_code}")
    return {"paused": True, "campaign": before["name"], "code": confirmation_code}


# ---------------------------------------------------------------------------
# 2. ENABLE CAMPAIGN
# ---------------------------------------------------------------------------

def enable_campaign(campaign_resource_name: str, confirmation_code: str) -> dict:
    """Enable (unpause) a campaign. Skips if already enabled."""
    _validate_code(confirmation_code, f"enable_campaign:{campaign_resource_name}")
    client, customer_id = _get_client()

    before = _get_campaign_current(client, customer_id, campaign_resource_name)
    _rollback_log("enable_campaign", before)

    if before["status"] == "ENABLED":
        _log(f"SKIP: {before['name']} already ENABLED")
        return {"skipped": True, "reason": "already_enabled", "campaign": before["name"]}

    campaign_svc = client.get_service("CampaignService")
    campaign = client.get_type("Campaign")
    campaign.resource_name = campaign_resource_name
    campaign.status = client.enums.CampaignStatusEnum.ENABLED
    op = client.get_type("CampaignOperation")
    op.update.CopyFrom(campaign)
    op.update_mask.paths.append("status")

    _mutate(
        lambda: campaign_svc.mutate_campaigns(customer_id=customer_id, operations=[op]),
        f"enable_campaign:{before['name']}"
    )
    _log(f"ENABLED: {before['name']} | code:{confirmation_code}")
    return {"enabled": True, "campaign": before["name"], "code": confirmation_code}


# ---------------------------------------------------------------------------
# 3. UPDATE DAILY BUDGET
# ---------------------------------------------------------------------------

def set_budget(budget_resource_name: str, new_daily_inr: float, confirmation_code: str) -> dict:
    """Update a campaign's daily budget. Max single change: configured % in config.yaml."""
    _validate_code(confirmation_code, f"set_budget:{budget_resource_name}")

    if new_daily_inr <= 0:
        raise ValueError("Budget must be positive.")

    config = _load_config()
    max_change_pct = config.get("thresholds", {}).get("budget_change_max_pct", 50)

    client, customer_id = _get_client()
    before = _get_budget_current(client, customer_id, budget_resource_name)
    _rollback_log("set_budget", before)

    current_inr = before["amount_inr"]

    if current_inr == new_daily_inr:
        _log(f"SKIP: Budget already at {new_daily_inr}")
        return {"skipped": True, "reason": "already_at_target"}

    if current_inr > 0:
        change_pct = abs(new_daily_inr - current_inr) / current_inr * 100
        if change_pct > max_change_pct:
            raise ValueError(
                f"Budget change of {round(change_pct)}% exceeds {max_change_pct}% limit.\n"
                f"Current: {current_inr} -> Proposed: {new_daily_inr}.\n"
                "Split into multiple smaller adjustments."
            )

    new_micros = round(new_daily_inr * 1_000_000)

    budget_svc = client.get_service("CampaignBudgetService")
    budget = client.get_type("CampaignBudget")
    budget.resource_name = budget_resource_name
    budget.amount_micros = new_micros
    op = client.get_type("CampaignBudgetOperation")
    op.update.CopyFrom(budget)
    op.update_mask.paths.append("amount_micros")

    _mutate(
        lambda: budget_svc.mutate_campaign_budgets(customer_id=customer_id, operations=[op]),
        f"set_budget:{before['name']}"
    )
    _log(f"BUDGET SET: {before['name']} | {current_inr} -> {new_daily_inr} | code:{confirmation_code}")
    return {
        "updated": True,
        "budget_name": before["name"],
        "before_inr": current_inr,
        "after_inr": new_daily_inr,
        "code": confirmation_code,
    }


# ---------------------------------------------------------------------------
# 4. UPDATE BID STRATEGY
# ---------------------------------------------------------------------------

def set_bid_strategy(
    campaign_resource_name: str,
    strategy: str,
    confirmation_code: str,
    target_cpa_inr: float = None,
) -> dict:
    """
    Update campaign bid strategy.
    strategy: MAXIMIZE_CLICKS | MAXIMIZE_CONVERSIONS | TARGET_CPA
    target_cpa_inr: required when strategy = TARGET_CPA
    """
    _validate_code(confirmation_code, f"set_bid_strategy:{campaign_resource_name}:{strategy}")

    valid_strategies = ["MAXIMIZE_CLICKS", "MAXIMIZE_CONVERSIONS", "TARGET_CPA"]
    if strategy not in valid_strategies:
        raise ValueError(f"Invalid strategy '{strategy}'. Options: {valid_strategies}")
    if strategy == "TARGET_CPA" and not target_cpa_inr:
        raise ValueError("target_cpa_inr is required when strategy is TARGET_CPA.")

    client, customer_id = _get_client()

    # Read and log actual current bid strategy before touching anything
    before = _get_bid_strategy_current(client, customer_id, campaign_resource_name)
    _rollback_log("set_bid_strategy", before)

    campaign_svc = client.get_service("CampaignService")
    campaign = client.get_type("Campaign")
    campaign.resource_name = campaign_resource_name

    if strategy == "MAXIMIZE_CLICKS":
        campaign.maximize_clicks.CopyFrom(client.get_type("MaximizeClicks"))
        mask_field = "maximize_clicks"
    elif strategy == "MAXIMIZE_CONVERSIONS":
        campaign.maximize_conversions.CopyFrom(client.get_type("MaximizeConversions"))
        mask_field = "maximize_conversions"
    elif strategy == "TARGET_CPA":
        tcpa = client.get_type("TargetCpa")
        tcpa.target_cpa_micros = round(target_cpa_inr * 1_000_000)
        campaign.target_cpa.CopyFrom(tcpa)
        mask_field = "target_cpa"

    op = client.get_type("CampaignOperation")
    op.update.CopyFrom(campaign)
    op.update_mask.paths.append(mask_field)

    _mutate(
        lambda: campaign_svc.mutate_campaigns(customer_id=customer_id, operations=[op]),
        f"set_bid_strategy:{before['name']}:{strategy}"
    )

    detail = f" (target CPA: {target_cpa_inr})" if target_cpa_inr else ""
    _log(
        f"BID STRATEGY SET: {before['name']} | "
        f"{before['bidding_strategy_type']} -> {strategy}{detail} | "
        f"code:{confirmation_code}"
    )
    return {
        "updated": True,
        "campaign": before["name"],
        "before": before["bidding_strategy_type"],
        "after": strategy,
        "target_cpa_inr": target_cpa_inr,
        "code": confirmation_code,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("execute.py — do not run directly from CLI.")
    print("Addy calls these functions after your confirmation.")
    print("Every call requires a council code (ADY-YYYYMMDD-XXX) matching today's date.")
