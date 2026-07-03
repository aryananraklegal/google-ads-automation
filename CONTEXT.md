# CONTEXT.md — Self-Learning Campaign Intelligence

> **Maintained by:** Claude (updated end of each session by LLM agent)
> **Purpose:** Carry forward what was decided, what happened, what works, and what to test next. Zero inferences — only confirmed facts and explicit decisions.
> **Format:** Append-only within sections. Newest entries first. Never delete — mark outdated entries as `[SUPERSEDED]`.

---

## 1. Decisions Log
*What was decided, what changed, and when.*

### 2026-07-03 (v3 — Jarvis rating fixes)
- **Jarvis/hallucination/convenience council ran — overall 5.5/10.** Three critical gaps identified.
- **RESEARCH.md rewritten — hallucination ban enforced:** All industry benchmark claims from training knowledge prohibited. Research now covers only: own account metrics (api.get_metrics()), own search terms, own asset labels, own conversion health. Competitor/benchmark sections only permitted with a live fetched URL cited inline. Market Expert in COUNCIL.md restricted to own account data only — banned from citing "typical India B2B SaaS CPAs" without a source.
- **monitor.py created — push alerting:** Cron-schedulable script that calls api.py, checks thresholds from config.yaml, and sends email alerts when kill rules, CTR drops, conversion action outages, or disapprovals are detected. Fires even when operator is not in a session. Forward projection included — warns 48h before kill rule evaluation window opens.
- **SETUP.md created — OAuth documented end to end:** Full step-by-step from Google Cloud project creation → API enablement → OAuth credential creation → auth flow → refresh token capture → google-ads.yaml format. Includes troubleshooting table for common errors. Estimated setup time: 30–45 minutes.
- **validate_config.py created:** Session-start config gate. Checks all required config.yaml fields, flags blank budget_resource entries, blocks on placeholder values, and catches manager account ID. Integrated into /ads skill as Step 1 before any API calls.
- **DAILY.md updated:** Added mandatory Step 5 — Forward Projection. Addy must project 48h ahead every session: days until kill rule evaluation, days until bidding phase gate opens, days since last research run. Added explicit rule: CONTEXT.md facts treated as starting context only, not ground truth — always verify with live API call before acting.
- **config.yaml updated:** Added notifications block (email SMTP config for push alerts, disabled by default).
- **Target rating post-v3 fixes: 7.5–8/10**

### 2026-07-03 (v2 — post council review + universal rebuild)
- **5-expert LLM council ran — DO NOT SHIP verdict (4.5/10):** Critical failures: zero error handling on API calls, `set_bid_strategy` rollback was a placeholder, `/ads` skill path wrong, kill rules calibrated for Search not PMax.
- **Universal rebuild completed:** System redesigned for any account on any machine — no hardcoded Windows paths, no hardcoded customer IDs, no machine-specific state.
- **config.yaml introduced:** Single source of truth for all account constants (customer ID, campaign resource names, conversion IDs, thresholds). `config.yaml.example` committed; real `config.yaml` gitignored.
- **api.py rebuilt:** Full error handling (GoogleAdsException, TransportError, RefreshError), date validation, GAQL injection prevention, cross-platform paths. New `get_bidding_phase_status()` added — returns rolling 30-day conversion count per campaign for council gate checks.
- **execute.py rebuilt:** All 4 write functions now read and log actual current state before mutating. `set_bid_strategy` now calls `_get_bid_strategy_current()` — no more placeholder rollback. Confirmation code validation enforces today's date + single-use within session. `round()` used for micros conversion (fixes float precision bug). `_mutate()` wrapper catches all Google Ads exceptions.
- **Skill path fixed:** Moved to `.claude/skills/ads/SKILL.md` (correct Claude Code registration path). Old `skills/ads/SKILL.md` is now superseded.
- **Kill rules recalibrated for PMax:** Old rule (3x CPA with 0 conversions) was calibrated for Search and would kill every PMax mid-learning-phase. New rule: pause only after minimum 14 days AND minimum spend threshold (3,000 INR students / 5,000 INR lawyers) both met.
- **Bidding phase gate fixed:** Rolling 30-day window enforced (not total conversions). Council Conversion Expert required to call `api.get_bidding_phase_status()` before any bid strategy change.
- **INTERVIEW.md created:** Campaign brief questionnaire Addy runs before every new campaign. Was referenced in CAMPAIGN.md but didn't exist.
- **Negative keyword list expanded:** Added India-specific legal market waste terms (UPSC, CLAT, LLB admission, judicial services, property dispute, NRI legal, court fee, vakil, legal aid, pro bono).
- **gitignore fixed:** `*.yaml` was blocking `config.yaml` from being tracked — replaced with specific entries: `config.yaml` ignored (real account data), `config.yaml.example` explicitly allowed.
- **Target rating post-rebuild: 8/10** (pending live API test to confirm error handling behaviour in practice).

### 2026-07-03 (v1)
- **Conversion tracking fix (PR #84) — STATUS: PENDING MERGE:** Moved student signup conversion event from onboarding form submit → `/onboarding` page load. Added `transaction_id: user.id` for Google-side deduplication. Added `onSuccess` callback to `OnboardingForm` to cover modal path (OnboardingCheck). Removed duplicate gtag block from `onboarding-form.tsx`. Removed deprecated `AW-17593778001` config from `layout.tsx`. PR raised against `anrakprojects/anraklegal2026`, awaiting approval from `anraktech` (Kapil). DO NOT resume campaigns until this is merged and beacon verified in prod.
- **Folder consolidation:** Merged `Google Ads/` folder into `google-ads-automation/`. Single working directory going forward.
- **Execution model confirmed:** Claude recommends → Kapil confirms in chat → Claude executes via Google Ads API.
- **System audit completed (rated 5/10):** Identified critical gaps — hardcoded Windows paths in `build_campaigns.py`, no idempotency, hidden execution scripts, duplicate scripts, council not enforced, no rollback capability.
- **Addy persona confirmed:** Female Google Ads operator. Warm, explains her thinking, walks Kapil through it. Invoked via "Hey Addy what's up" through a `/ads` Claude Code skill.
- **New architecture decided (pending build — spec approved):**
  - 5 Python scripts → 2 thin API connectors (`api.py` read-only, `execute.py` write-only)
  - All logic moves to `playbooks/` markdown files (DAILY.md, CAMPAIGN.md, OPTIMIZE.md, RESEARCH.md, COUNCIL.md)
  - `execute.py` requires council confirmation code before running — enforces NO-GO verdicts
  - `execute.py` idempotent — checks current state before every mutation
  - `execute.py` writes rollback log before every mutation
  - Session logs → `review/YYYY-MM-DD_session.md` | Permanent memory → `CONTEXT.md`
  - Session trigger: `/ads` skill in Claude Code loads Addy identity + CLAUDE.md + CONTEXT.md + yesterday's metrics
- **Target rating after rebuild: 9/10**

### 2026-07-01
- Both campaigns paused pending funnel strategy review.
- Diagnosed 0 conversions as funnel problem (not tracking bug) — users land on `/feed`, don't sign up.
- Confirmed lawyer conversion fires correctly via HAR test.

---

## 2. Account Learnings
*What works and what doesn't for Anrak's specific audience. Confirmed by data, not assumption.*

### Audience
- **99.8% mobile traffic** on both campaigns — desktop is negligible. Every landing page and creative must be designed mobile-first.
- **India B2B legal SaaS**: CPCs are low (₹1.01 students, ₹1.42 lawyers) but traffic is display/YouTube mix — lower intent than pure search.
- **Students convert differently than lawyers** — students browse content, lawyers look for demos/contact.

### Funnel
- **Content-first landing (`/feed`) produces 0 signups** — users read and leave. Needs a strong CTA or a gated element to drive signup.
- **`/chat` is public** — users can try the product without signing up, removing urgency to create an account.
- **Onboarding form friction is high** — 7 required fields including role-specific fields and practice area multi-select. Mobile UX risk.

### PMax
- **No audience signals = broad low-intent traffic.** PMax needs customer list or pixel audience to be effective.
- **No search themes = cold optimization.** Algorithm had no guidance on what queries to target.

### Conversion Tracking
- **Tag `AW-17980494112` confirmed correct** under account `2183727993`.
- **Conversion label `cqpwCLDpzsQcEKCi4v1C`** confirmed under correct account (verified in Google Ads UI, 2026-07-03).
- **Count = "One conversion"** in Google Ads settings — Google deduplicates per click on their side.

---

## 3. Outcomes
*What we ran, what the numbers showed.*

### Campaign 02 — PMax-Students + PMax-Lawyers (Jun 25–28 2026)

| Metric | Students | Lawyers |
|---|---|---|
| Spend | ₹1,739 | ₹796 |
| Impressions | 16,687 | 7,546 |
| Clicks | 1,723 | 559 |
| CTR | ~10.3% | ~7.4% |
| Avg CPC | ₹1.01 | ₹1.42 |
| Conversions | 0 | 0 |
| Device split | 99.8% mobile | 99.8% mobile |

**Why 0 conversions:**
- Students: landing on `/feed` (public content page), no signup prompt, users browse and leave
- Lawyers: contact form path was functional but no lawyers filled it
- Root cause is funnel drop-off, not broken tracking

### Campaign 01 — Search (May–Jun 2026)
- Spend: ₹6,273 · Clicks: 162 · CTR: 6.44% · Avg CPC: ₹38.72 · Conversions: 0
- Higher CPC (search intent) but same 0 conversion outcome — confirmed funnel issue predates Campaign 02

---

## 4. Hypotheses
*What to test next, ranked by confidence. Mark as [TESTED] once run.*

### High confidence
1. **CTA on `/feed`** — adding a sticky signup CTA or gating content after N articles will directly address the drop-off. Low effort, high impact.
2. **Audience signals on PMax** — uploading a customer list (existing signups) will significantly improve targeting quality. Required before Campaign 03.
3. **Search themes on PMax** — providing 10–15 seed keywords will stop cold optimization. Required before Campaign 03.

### Medium confidence
4. **Shorter onboarding form** — reducing required fields (especially practice areas) on mobile may increase form completion rate. Test: make practice areas optional.
5. **`/chat` soft gate** — limit unauthenticated users to 2–3 messages before prompting signup. Forces the decision without hard blocking.
6. **Lawyer-specific landing page** — dedicated page for lawyer campaign instead of homepage, with demo CTA and social proof (law firm logos).

### Low confidence / needs research
7. **India-specific PMax benchmarks** — need research sprint on what CTR/CPA targets are realistic for Indian legal B2B SaaS before setting Campaign 03 targets.
8. **Time-of-day optimization** — 9 AM–6 PM IST schedule is assumed correct for B2B. Validate with actual impression share data once campaigns resume.
