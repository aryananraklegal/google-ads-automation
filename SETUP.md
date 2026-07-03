# SETUP.md — Getting Addy Running

This guide takes you from zero to a working Addy session.
Estimated time: 30–45 minutes (most of that is Google's OAuth flow).

---

## Prerequisites

- Python 3.9+
- A Google Ads account (sub-account ID, not manager account)
- Access to Google Cloud Console for your organisation

---

## Step 1 — Install dependencies

```bash
pip install google-ads pyyaml
```

Verify:
```bash
python -c "from google.ads.googleads.client import GoogleAdsClient; print('OK')"
```

---

## Step 2 — Google Ads API credentials (OAuth)

This is the only complex step. Follow exactly.

### 2a. Create a Google Cloud project
1. Go to https://console.cloud.google.com
2. Create a new project (e.g. "Addy Google Ads")
3. Search for "Google Ads API" in the API library → Enable it

### 2b. Create OAuth credentials
1. Go to APIs & Services → Credentials → Create Credentials → OAuth client ID
2. Application type: **Desktop app**
3. Name it "Addy"
4. Download the JSON file — save it somewhere safe (not in this repo)

### 2c. Get your developer token
1. Go to Google Ads UI → Tools → API Centre
2. Apply for a developer token (Basic Access is enough for one account)
3. Copy the token

### 2d. Run the auth flow

```bash
python -c "
from google_auth_oauthlib.flow import InstalledAppFlow
import json, yaml, os

# Path to the OAuth JSON you downloaded in step 2b
client_secrets = input('Path to OAuth JSON file: ')

flow = InstalledAppFlow.from_client_secrets_file(
    client_secrets,
    scopes=['https://www.googleapis.com/auth/adwords']
)
creds = flow.run_local_server(port=0)

print()
print('Your refresh token (save this):')
print(creds.refresh_token)
"
```

A browser window opens. Log in with the Google account that has access to your Ads account.
Copy the refresh token printed at the end.

### 2e. Create secrets/google-ads.yaml

```bash
mkdir secrets
```

Create `secrets/google-ads.yaml` with this content:

```yaml
developer_token: YOUR_DEVELOPER_TOKEN
client_id: YOUR_CLIENT_ID          # from the OAuth JSON
client_secret: YOUR_CLIENT_SECRET  # from the OAuth JSON
refresh_token: YOUR_REFRESH_TOKEN  # from step 2d
use_proto_plus: True
```

**Never commit this file. It is gitignored.**

---

## Step 3 — Set up local files

```bash
cp config.yaml.example config.yaml
cp BELIEFS.md.example BELIEFS.md
cp CONTEXT.md.example CONTEXT.md
mkdir -p visuals/brand visuals/generated visuals/screenshots
```

- `config.yaml` — your account config (gitignored, stays local)
- `BELIEFS.md` — Addy's standing knowledge, starts blank, she builds it up over sessions (gitignored)
- `CONTEXT.md` — Addy's session log, starts blank (gitignored)
- `visuals/` — folder for brand assets and generated creatives

Drop your logo and brand screenshots into `visuals/brand/`.

Edit config.yaml:
- `account.customer_id` — find this in Google Ads UI, top right (format: 123-456-7890, enter without dashes)
- Campaign resource names — run `python api.py campaigns` after Step 4 to get these
- Conversion action IDs — run `python api.py conversions` after Step 4

For budget resource names (needed for set_budget):
- Google Ads UI → Campaigns → click the budget amount → URL contains the budget ID

---

## Step 4 — Validate connection

```bash
python api.py campaigns
```

Expected output: a list of your campaigns with status and budget.

If you see an error:
- `AuthenticationError` → check refresh_token and client credentials in google-ads.yaml
- `AuthorizationError` → check customer_id (must be sub-account, not manager account)
- `FileNotFoundError` → check secrets/ path

---

## Step 5 — Fill campaign resource names in config.yaml

From the `python api.py campaigns` output, copy the resource names and budget resource names into config.yaml.

Then validate everything is wired:
```bash
python api.py conversions   # should show your conversion actions as ENABLED
python api.py metrics       # should show yesterday's data (or empty if no spend)
```

---

## Step 6 — Start Addy

Open Claude Code in this folder:
```bash
cd path/to/google-ads-automation
claude
```

Say: **"Hey Addy what's up"**

---

## Push Alerting (optional but recommended)

Addy monitors continuously when configured. Alerts fire even when you're not in a session.

### Add to config.yaml:

```yaml
notifications:
  email:
    enabled: true
    to: "you@yourcompany.com"
    from: "addy-alerts@yourcompany.com"
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    smtp_user: "addy-alerts@yourcompany.com"
    smtp_password: "your-app-password"   # Gmail: use App Password, not account password
```

### Schedule monitor.py

**Windows (Task Scheduler):**
```
Action: python C:\path\to\google-ads-automation\monitor.py
Trigger: Daily, 8:00 AM
```

Or via PowerShell:
```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\google-ads-automation\monitor.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Addy Monitor"
```

**Mac/Linux (cron):**
```bash
# Run every morning at 8 AM IST (2:30 AM UTC)
30 2 * * 1-5 cd /path/to/google-ads-automation && python monitor.py >> review/cron.log 2>&1
```

Test it runs:
```bash
python monitor.py
```

Expected output: either "All clear" or a list of alerts. Check `review/YYYY-MM-DD_alerts.md`.

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `FileNotFoundError: config.yaml` | Not copied from example | `cp config.yaml.example config.yaml` |
| `FileNotFoundError: secrets/google-ads.yaml` | Credentials not placed | Follow Step 2 |
| `AuthenticationError` | Wrong refresh token or client creds | Re-run Step 2d |
| `AuthorizationError: Customer not found` | Using manager account ID | Use sub-account ID (not 7438563825) |
| `ValueError: Campaign not found` | Wrong resource name in config.yaml | Re-run `python api.py campaigns` and copy resource names |
| `set_budget fails with budget_resource` | budget_resource blank in config.yaml | Get budget ID from Google Ads UI URL |
