# COUNCIL.md — 4-Layer Review Process

> Every non-trivial change goes through council before execution.
> Council produces GO / NO-GO / GO WITH CONDITIONS + a confirmation code.
> execute.py will REJECT any call without a valid code matching today's date.
> One code = one action. Codes cannot be reused within a session.

---

## When Council Is Required

- Any budget change
- Any bid strategy change
- Enabling or launching a campaign
- Adding or removing negatives (bulk)
- New asset group creation
- Any change during active learning phase

## Confirmation Code Format
`ADY-YYYYMMDD-XXX`
- `YYYYMMDD` must match today's date exactly
- `XXX` is a sequential action ID for the session (001, 002, 003...)
- Example: `ADY-20260703-001`

---

## Pre-Council Data Pull (Addy always runs these first)

Before convening the council, Addy calls:
- `api.get_campaigns()` → current status and budgets
- `api.get_metrics()` for the last 14 days → trend data
- `api.get_bidding_phase_status()` → rolling 30-day conversion count per campaign
- `api.get_conversion_actions()` → verify tracking is ENABLED

Council experts receive this live data. They do not guess or use memory.

---

## Layer 1 — Domain Experts (run in parallel, each gets the live data)

### Budget Expert
Review the proposed change against live data:
- Is budget utilisation currently above or below 70%? (from metrics)
- Does the change respect the max % cap in config.yaml?
- Is the campaign in learning phase? (Never cut budget >20% during learning)
- Kill rule check: has minimum spend AND minimum days threshold been met before any pause?
  - Kill only evaluates after: min_days AND min_spend thresholds from config.yaml
  - Do NOT apply 3× CPA kill rule during PMax cold-start — algorithm is in discovery

Output: **SOUND / RISKY / BROKEN** + specific reason referencing the live data

### Creative Expert
- Are any assets rated "Low" for 7+ days? (from creatives report)
- Are all assets approved? Any disapprovals?
- Mobile-first check: images at 4:5 or 1:1 ratio?
- Headline/description character limit compliance?

Output: **SOUND / RISKY / N/A** + specific reason

### Conversion Expert
- Is the conversion action status ENABLED? (from conversion_actions data)
- What is the rolling 30-day conversion count per campaign? (from bidding_phase_status)
- Bid strategy gate:
  - MAXIMIZE_CLICKS → MAXIMIZE_CONVERSIONS: requires ≥15 conv in last 30 days
  - MAXIMIZE_CONVERSIONS → TARGET_CPA: requires ≥30 conv in last 30 days
  - If count is below threshold: BROKEN — do not approve bid strategy change
- Is the proposed change likely to trigger a new learning phase?

Output: **SOUND / RISKY / BROKEN** + specific count and threshold

### Market Expert
**HARD RULE: Only reason from the data sources below. No industry averages. No training-knowledge benchmarks. No "typically for India B2B SaaS." If a claim cannot be sourced to one of these, it is omitted.**

Data sources the Market Expert may use:
- `api.get_metrics()` historical data for this account (own CPCs, own CTRs, own spend patterns)
- CONTEXT.md Outcomes section (own historical campaign results)
- `api.get_search_terms()` — what queries are actually reaching the account
- Any URL explicitly fetched this session (cite the URL and retrieval date)

Questions to answer using only the above:
- Is the proposed CPA target achievable based on THIS account's own historical CPC and conversion rate?
  - Formula: If avg CPC = X and conversion rate = Y%, then CPA = X / Y%. Does the proposed target fit?
  - If we have 0 conversions historically, state: "No CPA history available — cannot validate target from own data."
- Does the change align with the 70/20/10 budget allocation rule? (check config.yaml campaigns list)
- Does the change make sense given the device split observed in our own metrics? (from api.get_metrics())
- Is the 70/20/10 budget allocation maintained across all campaigns after this change?

What the Market Expert does NOT do:
- Does not state what "typical India B2B SaaS CPAs" are
- Does not describe competitor activity without a live fetched URL
- Does not cite WordStream, SEMrush, or any benchmark report from memory

Output: **SOUND / RISKY / BROKEN** + specific reason citing the data source used

---

## Layer 2 — Executor (Addy)

Synthesise Layer 1 outputs.
- Any BROKEN = block advancement to Layer 3. State the blocker clearly.
- Draft the exact action (specific resource name from config.yaml, exact value, exact execute.py function call)
- No vague proposals. "Set budget to X" not "consider adjusting budget"

---

## Layer 3 — Critics

**Critic A — Risk:**
What is the worst realistic outcome if this goes wrong?
Is rollback possible from the rollback log alone?
Does the proposed action touch the learning phase?

**Critic B — Completeness:**
Is anything missing?
Are there downstream effects not accounted for?
Does this action require a corresponding action (e.g. enable campaign AND verify beacon first)?

---

## Layer 4 — Approver

Final verdict:

- **GO** — all experts SOUND, critics satisfied → generate confirmation code
- **GO WITH CONDITIONS** → state conditions explicitly. Generate code only after Kapil agrees to each condition.
- **NO-GO** → state blocker precisely. No code generated. What must change before re-submitting.

---

## Output Format

```
## Council Verdict: [GO / GO WITH CONDITIONS / NO-GO]

**Proposed action:** [exact description with resource names and values]

**Live data used:**
- Campaigns: [status from api.get_campaigns()]
- Conversions (30d): [count from api.get_bidding_phase_status()]
- Conversion tracking: [status from api.get_conversion_actions()]

| Expert | Rating | Reason |
|---|---|---|
| Budget | | |
| Creative | | |
| Conversion | | |
| Market | | |

**Critic A (Risk):** ...
**Critic B (Completeness):** ...

**Final rationale:** ...

**Confirmation code:** ADY-YYYYMMDD-XXX
```

If NO-GO: no confirmation code. State exactly what must be resolved first.
If GO WITH CONDITIONS: list each condition as a checkbox. Code generated only after each is confirmed.
