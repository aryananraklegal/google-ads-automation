# OPTIMIZE.md — When and How to Make Changes

> Addy uses this to decide WHEN to trigger council.
> All thresholds load from config.yaml at runtime — nothing is hardcoded here.
> No change happens without council. This doc defines the triggers.

---

## Change Triggers

### Trigger 1 — Budget Adjustment
**When:** Budget utilisation <70% for 3 consecutive days OR CPA < target by >10% for 7 days
**Action:** Propose budget change (within configured max % cap)
**Council required:** Yes

### Trigger 2 — Kill Rule (PMax-specific — do not apply early)
**When ALL of the following are true:**
- Flight duration ≥ `thresholds.kill.min_days` days (default 14)
- Spend ≥ `thresholds.kill.min_spend_inr` for this audience
- Conversions = 0

**NOT a kill trigger:**
- 0 conversions in the first 7 days — PMax is in discovery, this is normal
- 0 conversions with spend below minimum threshold — learning phase
- High CTR with 0 conversions before day 14 — could be audience signal working

**Action:** Propose pause
**Council required:** Yes (Budget Expert leads, confirms kill thresholds met)

### Trigger 3 — Bid Strategy Graduation
Check `api.get_bidding_phase_status()` for rolling 30-day conversion count.

| Current | Target | Gate |
|---|---|---|
| MAXIMIZE_CLICKS | MAXIMIZE_CONVERSIONS | ≥15 conv in last 30 days |
| MAXIMIZE_CONVERSIONS | TARGET_CPA | ≥30 conv in last 30 days |

**Action:** Propose bid strategy change
**Council required:** Yes — Conversion Expert must confirm rolling window count

### Trigger 4 — Asset Performance
**When:** Any asset rated "Low" for 7+ days
**Action:** Propose asset replacement
**Council required:** Yes — Creative Expert leads

### Trigger 5 — Audience Signal Update
**When:** Monthly — new signups can be added to customer list
**Action:** Export new users → upload to Google Ads audience
**Council required:** No (additive, no campaign mutation)

---

## What Addy Never Changes Without Being Asked
- Campaign targeting (geo, demographic, schedule)
- Negative keyword removals (additions only, removals need explicit instruction)
- Conversion action settings
- Asset group restructuring

---

## PMax-Specific Rules
- PMax allocates budget across Search, Display, YouTube, Gmail, Maps, Discover simultaneously
- Early CTR data reflects audience discovery, not funnel effectiveness — do not optimise creatives before day 14
- Search terms report may be sparse or missing in early days — this is expected
- Audience signals improve over time as the pixel builds — customer list upload is the fastest way to accelerate this

---

## Change Log (written by execute.py automatically)
Every executed change appears in `review/YYYY-MM-DD_session.md`:

```
[HH:MM:SS] ENABLED: PMax-Students-Jun2026 | code:ADY-20260703-001
[HH:MM:SS] BUDGET SET: PMax-Budget | 200 -> 240 | code:ADY-20260703-002
```

Rollback entries (before-state) written to `review/YYYY-MM-DD_rollback.md` before every mutation.
