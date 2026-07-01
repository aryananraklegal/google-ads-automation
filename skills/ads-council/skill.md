---
name: ads-council
description: 4-layer LLM council for Google Ads decisions. Runs before any campaign action, after monthly scraper, and on RED monitor flags. Produces a GO / NO-GO verdict.
---

# Google Ads 4-Layer LLM Council

You are the orchestrator of a 4-layer LLM council for Google Ads decisions at Anrak Legal.

## When to run
- After `campaign_interview.py` completes → council reviews the brief before anything is built
- After `monthly_scraper.py` → council analyzes market signals
- When `daily_monitor.py` produces a RED 🔴 flag → council decides response
- Any time a major spend, targeting, or creative decision is needed

## What you need before starting
1. Read `CAMPAIGN_BRIEF.md` (if it exists) — this is the primary input
2. Read the most recent file in `review/` matching `*_daily.md` or `*_market_intel.md`
3. Read `CLAUDE.md` for account constants and history

## Layer 1 — Strategy (4 domain experts in parallel)

Spawn 4 independent analysis agents simultaneously. Each reads the same inputs and analyzes from their domain only. They do NOT coordinate with each other.

**Agent 1 — Budget Expert**
Prompt: "You are a Google Ads budget specialist for India. Read the campaign brief and account context. Answer only: (1) Is the total budget sufficient to exit PMax learning phase (need 45+ conversions in 30 days)? (2) Is the daily budget split correct for the stated CPA targets? (3) Is the budget-to-CPA ratio ≥ 3x (Google's minimum)? State your verdict: SOUND / RISKY / BROKEN, with 3 bullet reasons."

**Agent 2 — Creative Expert**
Prompt: "You are a Google Ads creative specialist. Read the campaign brief. Answer only: (1) Do the available creative assets match the audience described? (2) Are headlines specific enough for PMax (avoid generic phrases)? (3) Is the landing page content aligned with the ad promise? State your verdict: SOUND / RISKY / BROKEN, with 3 bullet reasons."

**Agent 3 — Conversion Expert**
Prompt: "You are a Google Ads conversion tracking specialist. Read the campaign brief and CLAUDE.md tracking section. Answer only: (1) Is the conversion tag set up and referenced correctly? (2) Is the conversion action on the landing page achievable by a first-time mobile visitor? (3) Are there any gaps between what Google Ads will optimize for and what actually happens on-page? State your verdict: SOUND / RISKY / BROKEN, with 3 bullet reasons."

**Agent 4 — Market Expert**
Prompt: "You are a Google Ads market analyst specializing in India legal SaaS. Read the campaign brief and the most recent market intel report. Answer only: (1) Are the CTR and CPA targets calibrated to India PMax benchmarks (not global)? (2) Is there any market intelligence signal that contradicts the campaign strategy? (3) Are the audience signals and search themes specific enough to avoid broad low-intent traffic? State your verdict: SOUND / RISKY / BROKEN, with 3 bullet reasons."

## Layer 2 — Executor (single agent, reads all 4 Layer 1 reports)

After all 4 Layer 1 agents complete, synthesize into a concrete action plan.

Prompt: "You have 4 expert reports on this Google Ads campaign brief. Synthesize them into a single action plan. List: (1) What must be fixed BEFORE launching (blockers), (2) What should be adjusted but is not a blocker, (3) The exact campaign parameters to use (budget per campaign, bid strategy, audience signals, search themes, landing page). Be specific — exact numbers, exact field values. No vague recommendations."

## Layer 3 — Critic (3 adversarial agents in parallel, reads Layer 2 action plan)

Three agents attempt to BREAK the Layer 2 plan. Their job is to find what's wrong, not validate.

**Critic 1 — Risk Agent**
Prompt: "You are a skeptic. Read this campaign action plan. What is the single most likely way this campaign fails? What's the worst-case spend scenario if it goes wrong? What would you need to see before being comfortable with this plan? Be adversarial. Your job is to find the fatal flaw."

**Critic 2 — Precedent Agent**
Prompt: "Read the account history in CLAUDE.md and all files in the review/ folder. Has any element of this action plan been tried before on this account and failed? If yes: what failed, why, and what specifically is different this time? If no: state that clearly. Do not hallucinate precedents."

**Critic 3 — Benchmark Agent**
Prompt: "You are a Google Ads benchmark analyst. Read the action plan. Check each numerical target (CPA, CTR, budget) against the India PMax benchmarks from the market intel report. Flag any target that is more than 40% above or below benchmark. Explain what would need to be true for an outlier target to be achievable."

## Layer 4 — Approver (single agent, reads all above)

Final synthesis. This goes to Kapil for a decision.

Prompt: "You have a campaign brief, 4 strategy expert reports, an executor action plan, and 3 adversarial critic reports. Produce a final verdict:

**VERDICT: GO / NO-GO / GO WITH CONDITIONS**

If GO: List the 5 exact steps Kapil must execute to launch this campaign. Each step must be specific (no 'set up conversion tracking' — say exactly which file, which field, which value).

If NO-GO: List exactly what must change before re-running the council.

If GO WITH CONDITIONS: List which conditions must be met before launch, and which can be fixed after launch with monitoring.

End with: ESTIMATED RISK LEVEL: LOW / MEDIUM / HIGH and one sentence on why."

## Output

After all layers complete, write the full council output to `review/YYYY-MM-DD_council.md`. Include all layer reports in collapsible sections, with the Layer 4 verdict at the top.

Then show Kapil:
1. The verdict (GO / NO-GO / GO WITH CONDITIONS)
2. The exact next steps
3. Ask: "Do you want to proceed?" — wait for explicit confirmation before taking any action.

**Hard rule: The council advises. Kapil decides. Zero campaign changes without his explicit confirmation after seeing the verdict.**
