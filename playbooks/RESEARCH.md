# RESEARCH.md — Monthly Market Intelligence

> **HARD RULE: Addy never cites industry benchmarks, competitor CPAs, or market averages from training knowledge.**
> Every number in a research report must come from one of three sources:
> 1. Live api.py data (own account history)
> 2. A URL explicitly fetched in this session and cited inline
> 3. CONTEXT.md historical outcomes (own confirmed data)
>
> If a source cannot be cited with a live URL or api.py call, the finding is omitted.
> "Industry average" and "typical for India B2B SaaS" are banned phrases.

---

## What Addy Actually Researches (and how)

### 1. Own Account Benchmarks (ALWAYS — no external source needed)
Call `api.get_metrics(start, end)` across all prior campaign date ranges.
Pull from CONTEXT.md Outcomes section for all historical data.

Report:
- Our historical CTR by campaign and audience
- Our historical CPC by campaign and audience
- Our historical CPA (spend / conversions) where conversions > 0
- Trend: improving, stable, or declining vs prior period

This is the only benchmark that matters for bidding decisions.

### 2. Search Term Quality (ALWAYS)
Call `api.get_search_terms()` for last 30 days.
Categorise each term: high-intent / low-intent / off-brand.
Flag any off-brand terms not yet in the negative list.
Propose additions to the negative list.

### 3. Asset Performance (ALWAYS)
Call `api.get_creatives()` for last 30 days.
List all "Low" labelled assets. Flag for replacement.
List all "Good" and "Best" assets. Note what they have in common.

### 4. Conversion Tracking Health (ALWAYS)
Call `api.get_conversion_actions()`.
Confirm all conversion actions are ENABLED.
Cross-reference with CONTEXT.md to confirm no changes since last session.

### 5. Competitor Intelligence (CONDITIONAL — only with live URL)
Addy may only report competitor activity if she fetches a live URL in this session.
Use WebSearch or WebFetch if available. If neither is available, this section is skipped entirely.
Do not describe competitor features, pricing, or ad copy from training knowledge.

If web tools are available:
- Search: "[competitor name] Google Ads" + "[competitor name] pricing 2026"
- Cite the URL and date retrieved for every claim
- Only report what is on the page — no inference

If web tools are not available:
Write: "Competitor section skipped — no live web retrieval available this session. Check Google Ads Auction Insights report in the UI for impression share data."

### 6. Google Policy / Platform Updates (CONDITIONAL — only with live URL)
Same rule: only with a fetched URL. Otherwise skipped.
Suggested search: "Google Ads PMax updates 2026 site:blog.google OR site:support.google.com"

---

## Output Template

```md
# Research Report: [Month YYYY]
Generated: [date]
Data sources used: [list api.py calls made + any URLs fetched]

## Own Account Performance
[From api.get_metrics() — cite date range]

## Search Term Quality
[From api.get_search_terms() — cite date range]
Proposed negative additions: [list]

## Asset Performance
[From api.get_creatives()]
Low-performing assets to replace: [list]

## Conversion Tracking
[From api.get_conversion_actions()]
Status: [HEALTHY / FLAG]

## Competitor Intelligence
[Only if web tools used — cite URLs]
OR: "Skipped — no live web retrieval available."

## Recommended Actions
[Only actions grounded in the above data]
1. ...
```

Save to `review/YYYY-MM_research.md`.
Summarise grounded findings only in CONTEXT.md under Account Learnings.
