"""
monitor.py — Addy's push alerting engine.

Runs on a schedule (cron / Task Scheduler). Checks live campaign data against
thresholds in config.yaml. Sends a notification if anything needs attention.

Zero hallucination: every alert is grounded in live api.py data.
No action taken — read-only. Addy still requires operator confirmation to act.

Setup:
  See SETUP.md → "Push Alerting" section.
  Configure notification method in config.yaml → notifications block.
"""

import json
import smtplib
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).parent
TODAY = datetime.today().strftime("%Y-%m-%d")
OUTPUT_DIR = ROOT / "review"
OUTPUT_DIR.mkdir(exist_ok=True)
ALERT_LOG = OUTPUT_DIR / f"{TODAY}_alerts.md"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def _load_config() -> dict:
    import yaml
    config_path = ROOT / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found.")
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Alert builder
# ---------------------------------------------------------------------------

class Alert:
    def __init__(self, level: str, campaign: str, metric: str, value, threshold, message: str):
        self.level = level       # CRITICAL / WARNING / INFO
        self.campaign = campaign
        self.metric = metric
        self.value = value
        self.threshold = threshold
        self.message = message

    def __str__(self):
        return f"[{self.level}] {self.campaign} | {self.metric}: {self.value} (threshold: {self.threshold}) — {self.message}"


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def _check_metrics(metrics_data: dict, config: dict) -> list[Alert]:
    alerts = []
    t = config.get("thresholds", {})
    cpa_targets = t.get("cpa_targets", {})
    kill = t.get("kill", {})

    # Audience names come from config campaigns (e.g. "students", "lawyers", "shoppers"),
    # not hardcoded — keeps monitor.py account-agnostic. Threshold keys are built per
    # audience (e.g. cpa_targets.<audience>_inr, kill.<audience>_min_spend_inr) with
    # generic fallbacks, so an unrecognised audience still gets sane defaults.
    known_audiences = {
        str(c.get("audience", "")).rstrip("s").lower()
        for c in config.get("campaigns", []) if c.get("audience")
    }
    for camp in metrics_data.get("campaigns", []):
        name = camp["campaign"]
        audience = next((a for a in known_audiences if a and a in name.lower()), None)

        # Budget utilisation — flag if spend is very low (api doesn't return budget directly,
        # so we flag 0 spend as a proxy for paused/starved campaign)
        if camp["clicks"] == 0 and camp["impressions"] == 0 and camp["status"] == "ENABLED":
            alerts.append(Alert(
                "WARNING", name, "spend", 0, ">0",
                "Campaign is ENABLED but got 0 clicks and 0 impressions. May be disapproved or misconfigured."
            ))

        # CTR check
        ctr = camp["ctr_pct"]
        ctr_threshold = 2.0 if audience == "student" else 1.0
        if camp["clicks"] > 50 and ctr < ctr_threshold:
            alerts.append(Alert(
                "WARNING", name, "CTR", f"{ctr}%", f">{ctr_threshold}%",
                f"CTR below threshold with {camp['clicks']} clicks. Creative or targeting may need review."
            ))

        # Zero conversions after meaningful spend
        spend = camp["cost_inr"]
        conv = camp["conversions"]
        min_spend = kill.get(f"{audience}_min_spend_inr", 3000)
        if conv == 0 and spend >= min_spend:
            alerts.append(Alert(
                "CRITICAL", name, "conversions", 0, f">0 after {min_spend} INR spend",
                f"Kill rule threshold reached: {spend} INR spent with 0 conversions. Review required."
            ))

        # CPA check (only if conversions > 0)
        if conv > 0:
            cpa = spend / conv
            cpa_target = cpa_targets.get(f"{audience}_inr", 300)
            if cpa > cpa_target * 2:
                alerts.append(Alert(
                    "CRITICAL", name, "CPA", f"{round(cpa, 0)} INR",
                    f">{cpa_target * 2} INR",
                    f"CPA is more than 2x target. Bid strategy review needed."
                ))

    return alerts


def _check_conversions(conversion_data: dict, config: dict) -> list[Alert]:
    alerts = []
    # Expected conversion action IDs come from config.yaml, not hardcoded — keeps
    # monitor.py account-agnostic. Add every conversion you want tracking-monitored
    # under config.yaml `conversions:` with its `id`.
    expected_ids = {str(c["id"]) for c in config.get("conversions", []) if c.get("id")}
    if not expected_ids:
        return alerts  # nothing configured to check

    active = {str(ca["id"]) for ca in conversion_data.get("conversion_actions", [])
              if ca["status"] == "ENABLED"}

    for expected_id in expected_ids:
        if expected_id not in active:
            alerts.append(Alert(
                "CRITICAL", "Account", "conversion_action",
                f"ID {expected_id} not ENABLED", "ENABLED",
                "A conversion action is missing or paused. Tracking may be broken."
            ))

    return alerts


def _forward_projection(config: dict) -> list[Alert]:
    """
    Reads CONTEXT.md to find campaign launch dates and project upcoming decision points.
    Warns before thresholds are breached, not after.
    """
    alerts = []
    context_path = ROOT / "CONTEXT.md"
    if not context_path.exists():
        return alerts

    kill = config.get("thresholds", {}).get("kill", {})
    min_days = kill.get("min_days", 14)

    # Parse CONTEXT.md for campaign launch dates
    # Looks for lines containing "ENABLED:" in session logs
    for log_file in sorted(OUTPUT_DIR.glob("*_session.md")):
        try:
            log_date_str = log_file.name[:10]
            log_date = datetime.strptime(log_date_str, "%Y-%m-%d")
            days_running = (datetime.today() - log_date).days

            content = log_file.read_text(encoding="utf-8")
            if "ENABLED:" in content:
                days_to_kill_eval = min_days - days_running
                if 0 < days_to_kill_eval <= 2:
                    alerts.append(Alert(
                        "INFO", "Campaign", "kill_rule_evaluation",
                        f"Day {days_running}", f"Day {min_days}",
                        f"Kill rule evaluation window opens in {days_to_kill_eval} day(s). "
                        f"If conversions are still 0, be ready to discuss pausing."
                    ))
        except (ValueError, OSError):
            continue

    return alerts


# ---------------------------------------------------------------------------
# Notification dispatch
# ---------------------------------------------------------------------------

def _send_email(subject: str, body: str, config: dict):
    notif = config.get("notifications", {}).get("email", {})
    if not notif.get("enabled"):
        return

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"[Addy] {subject}"
    msg["From"] = notif["from"]
    msg["To"] = notif["to"]

    try:
        with smtplib.SMTP(notif["smtp_host"], notif.get("smtp_port", 587)) as server:
            server.starttls()
            server.login(notif["smtp_user"], notif["smtp_password"])
            server.send_message(msg)
        print(f"Email sent to {notif['to']}")
    except Exception as e:
        print(f"Email failed: {e}")


def _log_alerts(alerts: list[Alert]):
    lines = [f"# Alert Log: {TODAY}\n"]
    if not alerts:
        lines.append("No alerts. All metrics within thresholds.")
    else:
        for a in alerts:
            lines.append(str(a))
    content = "\n".join(lines)
    ALERT_LOG.write_text(content, encoding="utf-8")
    print(content)
    return content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    # Import here so monitor.py can be imported without api.py dependencies
    from api import get_metrics, get_conversion_actions

    config = _load_config()
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Addy monitor running for {yesterday}")

    alerts = []

    try:
        metrics = get_metrics(yesterday, yesterday)
        alerts += _check_metrics(metrics, config)
    except Exception as e:
        alerts.append(Alert("CRITICAL", "System", "api_metrics", "ERROR", "OK", str(e)))

    try:
        conversions = get_conversion_actions()
        alerts += _check_conversions(conversions, config)
    except Exception as e:
        alerts.append(Alert("CRITICAL", "System", "api_conversions", "ERROR", "OK", str(e)))

    alerts += _forward_projection(config)

    report = _log_alerts(alerts)

    criticals = [a for a in alerts if a.level == "CRITICAL"]
    warnings = [a for a in alerts if a.level == "WARNING"]

    if criticals or warnings:
        subject = f"{len(criticals)} CRITICAL, {len(warnings)} WARNING — action needed"
        _send_email(subject, report, config)
    else:
        print("All clear. No notifications sent.")

    return {"alerts": len(alerts), "criticals": len(criticals), "warnings": len(warnings)}


if __name__ == "__main__":
    try:
        result = run()
        sys.exit(0 if result["criticals"] == 0 else 1)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"ERROR: {e}")
        sys.exit(2)
