"""
Google Ads Automation — Setup Wizard
Run: python setup.py
Takes ~5 minutes. You will need:
  1. Your Google Ads developer token
  2. A Google Cloud project with OAuth 2.0 credentials
  3. Your Google Ads Customer ID (direct account, NOT manager)
"""
import sys
import os
import subprocess
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
SECRETS_DIR = os.path.join(ROOT, "secrets")
SECRETS_FILE = os.path.join(SECRETS_DIR, "google-ads.yaml")
CLAUDE_MD = os.path.join(ROOT, "CLAUDE.md")
CLAUDE_MD_TEMPLATE = os.path.join(ROOT, "CLAUDE.md.template")

def step(n, title):
    print(f"\n{'='*60}")
    print(f"  Step {n}: {title}")
    print(f"{'='*60}")

def ask(prompt, required=True):
    while True:
        val = input(f"\n{prompt}\n> ").strip()
        if val:
            return val
        if not required:
            return ""
        print("  This field is required.")

def confirm(prompt):
    while True:
        val = input(f"\n{prompt} [y/n] > ").strip().lower()
        if val in ("y", "yes"):
            return True
        if val in ("n", "no"):
            return False

def check_python():
    step(1, "Checking Python version")
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        print(f"  ERROR: Python 3.10+ required. You have {v.major}.{v.minor}.")
        sys.exit(1)
    print(f"  OK: Python {v.major}.{v.minor}.{v.micro}")

def install_deps():
    step(2, "Installing dependencies")
    print("  Running: pip install -r requirements.txt")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("  ERROR during install:")
        print(result.stderr[-500:])
        sys.exit(1)
    print("  OK: All dependencies installed.")

def gcp_instructions():
    step(3, "Google Cloud Project setup (one-time)")
    print("""
  You need a Google Cloud project with OAuth 2.0 credentials.
  This is a one-time setup. Follow these steps:

  3a. Go to https://console.cloud.google.com/
      - Create a new project (or select an existing one)

  3b. Enable the Google Ads API:
      - Go to APIs & Services > Library
      - Search "Google Ads API" and click Enable

  3c. Create OAuth 2.0 credentials:
      - Go to APIs & Services > Credentials
      - Click "Create Credentials" > "OAuth client ID"
      - Application type: Desktop app
      - Name: google-ads-automation
      - Click Create
      - Download the JSON file

  3d. OAuth consent screen:
      - Go to APIs & Services > OAuth consent screen
      - User type: External (or Internal if using Google Workspace)
      - Add scope: https://www.googleapis.com/auth/adwords
      - Add your email as a test user
""")
    input("  Press Enter when you have your Client ID and Client Secret ready...")

def collect_credentials():
    step(4, "Enter your credentials")
    print("""
  You will need:
  - Developer token: Google Ads > Admin > API Center
  - Client ID and Secret: from Google Cloud OAuth credentials JSON
  - Customer ID: your Google Ads account ID (format: 123-456-7890, enter digits only)
""")
    dev_token   = ask("Developer token (from Google Ads API Center):")
    client_id   = ask("Client ID (ends in .apps.googleusercontent.com):")
    client_secret = ask("Client secret:")
    customer_id = ask("Customer ID (digits only, e.g. 2183727993):").replace("-", "")
    return dev_token, client_id, client_secret, customer_id

def get_refresh_token(client_id, client_secret):
    step(5, "Authorize Google Ads access (OAuth2)")
    print("""
  We'll open a browser window for you to authorize access.
  After you authorize, you'll be redirected to a localhost page.
  Copy the full URL from your browser address bar and paste it here.
""")
    from google_auth_oauthlib.flow import InstalledAppFlow

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/adwords"]
    )

    print("  Opening browser for authorization...")
    try:
        credentials = flow.run_local_server(port=0, open_browser=True)
    except Exception as e:
        print(f"  Browser flow failed: {e}")
        print("  Trying manual URL method...")
        auth_url, _ = flow.authorization_url(prompt="consent")
        print(f"\n  Open this URL in your browser:\n  {auth_url}\n")
        webbrowser.open(auth_url)
        code = ask("Paste the authorization code from the redirect URL:")
        flow.fetch_token(code=code)
        credentials = flow.credentials

    print("  Authorization successful.")
    return credentials.refresh_token

def write_secrets(dev_token, client_id, client_secret, customer_id, refresh_token):
    step(6, "Writing credentials file")
    os.makedirs(SECRETS_DIR, exist_ok=True)
    yaml_content = f"""developer_token: {dev_token}
client_id: {client_id}
client_secret: {client_secret}
refresh_token: {refresh_token}
login_customer_id: "{customer_id}"
use_proto_plus: True
"""
    with open(SECRETS_FILE, "w") as f:
        f.write(yaml_content)
    print(f"  Credentials saved to secrets/google-ads.yaml")
    print("  IMPORTANT: This file is gitignored and will NEVER be committed.")

def write_claude_md(customer_id):
    step(7, "Generating CLAUDE.md")
    if not os.path.exists(CLAUDE_MD_TEMPLATE):
        print("  WARNING: CLAUDE.md.template not found. Skipping.")
        return
    with open(CLAUDE_MD_TEMPLATE, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("{{CUSTOMER_ID}}", customer_id)
    with open(CLAUDE_MD, "w", encoding="utf-8") as f:
        f.write(content)
    print("  CLAUDE.md generated. Open it and fill in your campaign details.")

def verify():
    step(8, "Verifying API connection")
    print("  Running a quick API test...")
    test_script = f"""
import sys, yaml
sys.stdout.reconfigure(encoding="utf-8")
from google.ads.googleads.client import GoogleAdsClient
with open(r"{SECRETS_FILE}") as f:
    cfg = yaml.safe_load(f)
client = GoogleAdsClient.load_from_dict(cfg)
ga = client.get_service("GoogleAdsService")
rows = list(ga.search(customer_id=cfg["login_customer_id"].strip('"'), query="SELECT campaign.name FROM campaign LIMIT 1"))
print(f"  OK: Connected. Found {{len(rows)}} campaign(s).")
"""
    tmp = os.path.join(ROOT, "_verify.py")
    with open(tmp, "w") as f:
        f.write(test_script)
    result = subprocess.run([sys.executable, tmp], capture_output=True, text=True, cwd=ROOT)
    os.remove(tmp)
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print("  WARNING: API test failed. Check your credentials.")
        print(result.stderr[-300:])

def done():
    print(f"""
{'='*60}
  Setup complete.

  Next steps:
  1. Open Claude Code in this folder:
       cd "{ROOT}"
       claude

  2. CLAUDE.md has been generated. Edit it to fill in your
     campaign details (budget, audience, goals).

  3. Run your first daily monitor:
       python scripts/daily_monitor.py

  4. Start a campaign:
       python scripts/campaign_interview.py

  The 4-layer LLM council will run automatically when
  creating or reviewing campaigns. Just follow the prompts.
{'='*60}
""")

if __name__ == "__main__":
    print("\n  Google Ads Automation — Setup Wizard")
    print("  =====================================")
    print("  This will take ~5 minutes.\n")

    check_python()
    install_deps()
    gcp_instructions()
    dev_token, client_id, client_secret, customer_id = collect_credentials()
    refresh_token = get_refresh_token(client_id, client_secret)
    write_secrets(dev_token, client_id, client_secret, customer_id, refresh_token)
    write_claude_md(customer_id)
    verify()
    done()
