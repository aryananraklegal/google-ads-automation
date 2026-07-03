# DAILY.md — Addy's Morning Check Routine

> Runs every session when the operator says "Hey Addy what's up."
> Entirely grounded in live data. No numbers from memory or training knowledge.

---

## Step 1 — Config Validation (before anything else)

Run `validate_config.py` checks mentally or explicitly:
- Is config.yaml fully populated? (No placeholder values)
- Are secrets/google-ads.yaml credentials present?
- Are budget_resource fields filled for all campaigns?

If any field is missing, state the gap clearly before proceeding.
Do not continue with a session if the config would cause a silent failure downstream.

---

## Step 2 — Load Memory

Read `CONTEXT.md` — decisions log, learnings, open hypotheses.
Note the date of the last session. Note any pending actions that weren't completed.

**IMPORTANT:** Treat CONTEXT.md facts as starting context, not ground truth.
Campaign status, conversion counts, and funnel details in CONTEXT.md can be stale.
Always verify with a live api.py call before acting on them.

---

## Step 3 — Pull Live Data

Run these in order. Every number in the brief comes from these calls:

```
api.get_campaigns()              → current status and budget of all campaigns
api.get_metrics(yesterday)       → clicks, impressions, spend, conversions
api.get_conversion_actions()     → confirm tracking is ENABLED
```

Do not estimate or recall yesterday's numbers. If the API call fails, say so and report the error.

---

## Step 4 — Threshold Check

Compare metrics against thresholds in config.yaml (loaded at runtime, not from CLAUDE.md).

Flag immediately if:
- Any ENABLED campaign: clicks = 0 AND impressions = 0 → likely disapproval or billing issue
- CTR below threshold with >50 clicks
- Conversion actions not ENABLED → tracking is broken, campaigns should not run
- Kill rule conditions met (min_days AND min_spend both exceeded with 0 conversions)
- Any asset rated "Low" for 7+ days (check api.get_creatives() if last check was >7 days ago)

---

## Step 5 — Forward Projection (mandatory — do not skip)

Look ahead 48 hours. State explicitly what becomes urgent:

- "Tomorrow is day [N] of [Campaign]. [X] more days until kill rule evaluation window opens."
- "Bid strategy gate opens at 15 conversions in 30 days. Current count: [N from api.get_bidding_phase_status()]."
- "Last research run was [date from CONTEXT.md]. Monthly research is due [date]."
- "PR #84 / [any open codebase item] — has this been confirmed deployed? If not, verify before resuming campaigns."

If nothing is upcoming, say: "Nothing urgent in the next 48 hours."

---

## Step 6 — Brief

Open with a concrete brief. Example:

> "Hey, good to be back. Yesterday: Students got 38 clicks at 1.12 CPC, 43 INR spent,
> 0 conversions. Lawyers: 9 clicks, 13 INR, 0 conversions. Conversion tracking is ENABLED
> on both actions. Nothing flagged yet — we're on day 4, still within normal PMax discovery.
>
> One thing to flag: tomorrow is day 13. If we still have 0 conversions by end of day,
> kill rule evaluation opens the day after. I'd recommend we have that conversation now
> rather than when we're at the threshold. Want to talk through options?"

Rules for the brief:
- Every number is sourced from Step 3
- No phrases like "typically" or "industry standard" or "usually"
- State the source if it could be ambiguous ("from yesterday's metrics", "from CONTEXT.md 2026-07-01")
- If data is missing (API error, no spend yet), say so explicitly

---

## Step 7 — Await Direction

Do not propose changes unprompted unless:
- A kill rule threshold is met → recommend pause, run council
- A conversion action is not ENABLED → flag as CRITICAL, recommend investigation
- An ad is disapproved → flag immediately

For everything else, surface the information and let the operator decide what to focus on.
