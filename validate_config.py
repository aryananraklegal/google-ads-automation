"""
validate_config.py — Run at session start to catch config gaps before they cause silent failures.

Called automatically when /ads skill loads.
Exits with a clear error message if anything is missing or wrong.
Never touches the API — config-only checks.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent


def validate() -> list[str]:
    """Returns a list of error strings. Empty list = all good."""
    errors = []

    # --- config.yaml exists ---
    config_path = ROOT / "config.yaml"
    if not config_path.exists():
        return ["config.yaml not found. Run: cp config.yaml.example config.yaml and fill it in. See SETUP.md."]

    try:
        import yaml
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        return [f"config.yaml is not valid YAML: {e}"]

    # --- secrets/google-ads.yaml exists ---
    secrets_path = ROOT / "secrets" / "google-ads.yaml"
    if not secrets_path.exists():
        errors.append(
            "secrets/google-ads.yaml not found. Follow SETUP.md Step 2 to create credentials."
        )

    # --- account.customer_id ---
    account = config.get("account", {})
    customer_id = account.get("customer_id", "")
    manager_id = str(account.get("manager_id", "") or "")
    if not customer_id or customer_id == "YOUR_CUSTOMER_ID":
        errors.append("config.yaml: account.customer_id is not set. Fill in your Google Ads sub-account ID.")
    elif manager_id and customer_id == manager_id:
        errors.append(
            f"config.yaml: account.customer_id is the MANAGER account ({manager_id}). "
            "This causes auth failure. Use the sub-account ID instead. "
            "(Set account.manager_id in config so Addy can catch this.)"
        )

    # --- campaigns ---
    campaigns = config.get("campaigns", [])
    if not campaigns:
        errors.append("config.yaml: no campaigns defined. Add at least one campaign entry.")

    for i, camp in enumerate(campaigns):
        label = camp.get("label", f"campaign[{i}]")

        rn = camp.get("resource_name", "")
        if not rn or "YOUR_CUSTOMER_ID" in rn or "CAMPAIGN_ID" in rn:
            errors.append(
                f"config.yaml: campaigns[{i}] ({label}) has a placeholder resource_name. "
                "Run `python api.py campaigns` to get real resource names."
            )

        budget_rn = camp.get("budget_resource", "")
        if not budget_rn or "BUDGET_ID" in budget_rn:
            errors.append(
                f"config.yaml: campaigns[{i}] ({label}) has no budget_resource. "
                "Get the budget ID from Google Ads UI (click the budget amount, check the URL) "
                "and set it as: customers/CUSTOMER_ID/campaignBudgets/BUDGET_ID"
            )

    # --- conversions ---
    conversions = config.get("conversions", [])
    if not conversions:
        errors.append("config.yaml: no conversion actions defined.")

    for i, conv in enumerate(conversions):
        if not conv.get("id") or conv.get("id") == "CONVERSION_ACTION_ID":
            errors.append(
                f"config.yaml: conversions[{i}] has a placeholder id. "
                "Run `python api.py conversions` to get real conversion action IDs."
            )

    # --- thresholds present ---
    thresholds = config.get("thresholds", {})
    if not thresholds:
        errors.append(
            "config.yaml: no thresholds defined. Copy from config.yaml.example."
        )
    else:
        kill = thresholds.get("kill", {})
        if not kill.get("min_days"):
            errors.append("config.yaml: thresholds.kill.min_days not set.")
        bidding = thresholds.get("bidding_phase", {})
        if not bidding.get("growth_min_conversions"):
            errors.append("config.yaml: thresholds.bidding_phase.growth_min_conversions not set.")

    return errors


def run_and_exit_on_error():
    errors = validate()
    if errors:
        print("\nAddy cannot start — config issues found:\n")
        for i, e in enumerate(errors, 1):
            print(f"  {i}. {e}")
        print("\nFix these in config.yaml then try again. See SETUP.md for help.")
        sys.exit(1)
    else:
        print("Config OK.")


if __name__ == "__main__":
    run_and_exit_on_error()
