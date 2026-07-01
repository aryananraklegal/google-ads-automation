# Google Ads Automation

A self-contained package for running high-frequency Google Ads campaigns with Claude Code. Built for Anrak Legal, usable by anyone.

**What it does:**
- Daily campaign monitoring with threshold flags
- Monthly market intelligence scraping
- Pre-campaign interview → structured brief
- 4-layer LLM council: GO / NO-GO verdict before any action

**What it does NOT do:**
- Make any campaign changes without your explicit confirmation
- Store your credentials or review data in this repo

---

## Install (5 minutes)

```bash
git clone https://github.com/anrakprojects/google-ads-automation
cd google-ads-automation
python setup.py
```

Setup wizard will:
1. Install dependencies
2. Walk you through Google Cloud OAuth setup (step-by-step)
3. Collect your credentials and write them locally
4. Generate a `CLAUDE.md` for your account
5. Verify the API connection

**Prerequisite:** Python 3.10+. That's it.

---

## Daily use

```bash
# Morning check
python scripts/daily_monitor.py

# New campaign (start here)
python scripts/campaign_interview.py

# Monthly (run once a month)
python scripts/monthly_scraper.py
```

Then open Claude Code in this folder: `claude`

The LLM council runs automatically when needed. Invoke manually with `/ads-council`.

---

## What you need from Google

1. **Developer token** — Google Ads > Admin > API Center
2. **Google Cloud project** with Google Ads API enabled (setup wizard walks you through this)
3. **OAuth 2.0 credentials** — Client ID + Secret from Google Cloud Console
4. **Customer ID** — your Google Ads account ID (not a manager account)

---

## Security

- `secrets/` is gitignored. Never committed.
- `review/` is gitignored. Local only.
- Scripts are read-only against the Google Ads API. Zero write calls.
- All campaign actions require explicit confirmation.

---

## Structure

```
scripts/          Python monitoring + interview scripts
skills/           Claude Code skills (domain experts + council)
references/       Benchmark docs, PMax guides
templates/        CAMPAIGN_BRIEF.md template
council/          Council orchestration logic
```
