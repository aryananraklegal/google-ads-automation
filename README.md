# Addy — Google Ads Operator

Addy is an AI-powered Google Ads operator built on Claude Code. She monitors your campaigns, surfaces what needs attention, runs a 4-layer council review before any change, and executes only after your explicit confirmation.

Built for AnrakLegal. Works for any Google Ads account.

---

## What Addy does

- Loads your account memory and live campaign data every session
- Flags threshold breaches, kill rule conditions, and conversion tracking issues
- Projects 48 hours ahead — warns before things go wrong, not after
- Runs a 4-layer LLM council (Budget / Creative / Conversion / Market experts) before every change
- Executes changes via Google Ads API with a date-locked confirmation code
- Logs every action with a rollback record before mutating
- Sends push alerts via email when campaigns need attention (even when you're not in a session)

## What Addy never does

- Makes any change without your explicit "yes"
- Cites industry benchmarks without a live source URL
- Uses the same confirmation code twice
- Touches the Google Ads API without a valid council code

---

## Setup

See **[SETUP.md](SETUP.md)** for the full guide. Estimated time: 30–45 minutes.

Short version:
```bash
pip install google-ads pyyaml
cp config.yaml.example config.yaml   # fill in your account details
# place google-ads.yaml in secrets/  # see SETUP.md for OAuth steps
python api.py campaigns               # verify connection
```

---

## Daily use

Open Claude Code in this folder:
```bash
claude
```

Say: **"Hey Addy what's up"**

That's it. Addy handles the rest.

---

## Push alerting (optional)

Schedule `monitor.py` to run daily — it checks live metrics and emails you if anything needs attention.

```bash
python monitor.py   # test it
```

See SETUP.md → "Push Alerting" for cron / Task Scheduler setup.

---

## Structure

```
CLAUDE.md               Addy's operating rules + account constants
CONTEXT.md              Addy's persistent memory (updated every session)
SETUP.md                First-time setup guide
config.yaml             Your account config (gitignored)
config.yaml.example     Template for new accounts
api.py                  Read-only Google Ads API connector
execute.py              Write connector (requires council code)
monitor.py              Push alerting engine
validate_config.py      Session-start config validation
playbooks/              Addy's operating procedures
  DAILY.md              Morning check routine
  INTERVIEW.md          Campaign brief questionnaire
  COUNCIL.md            4-layer review + confirmation code
  OPTIMIZE.md           Change triggers and decision framework
  CAMPAIGN.md           Build and launch checklist
  RESEARCH.md           Monthly market intelligence
.claude/skills/ads/     /ads skill (invokes Addy)
campaigns/              Campaign archives
references/             Static knowledge base
```

---

## Security

- `secrets/` is gitignored — credentials never committed
- `review/` is gitignored — outputs stay local
- `config.yaml` is gitignored — account IDs stay local
- Every write operation requires a council confirmation code matching today's date
- Confirmation codes are single-use — replay rejected in code
