# Campaign Brief — PMax-Students-Aug2026
**Generated:** 2026-07-02
**Last revised:** 2026-07-12 by Addy — synced with live Students PMax learnings post-resume (2026-07-06 onward)

## Flight
- **Dates:** 2026-08-01 → 2026-08-14
- **Total budget:** ₹14000
- **Budget split:** 70% Students / 30% Lawyers
- **Geography:** All India

## Goal
- **Conversion event:** student_signup
- **Target CPA:** ₹250
- **Conversion action on page:** Clicks sign up button > fills onboarding form > reaches /chat
- **Conversion tag:** AW-17980494112/cqpwCLDpzsQcEKCi4v1C
- **VALIDATED 2026-07-12:** the ₹250 target now has real data behind it, not just a guess. Students PMax has run ₹250 as an implicit ceiling since resuming 2026-07-06 and is currently converting at cumulative CPA ₹151.29 (29 conversions, 2026-07-06→11, live API). ₹250 is a safe target, not an aggressive one — consider ₹200 if council wants to tighten it.

## Audience
- **Who:** Indian law students in their final year preparing for moot court. They use Claude for research and need Indian case law access.
- **Audience signals:** Law students India, Legal AI users, Manupatra visitors
- **Search themes:** legal AI India, moot court research, Indian case law
- **NOTE 2026-07-12:** the signals/themes above are the original guesses from this brief's first draft (2026-07-02). The actual live Students PMax setup used on resume (2026-07-06) is a *different, more specific* spec — custom search-intent segment + ICP-website segment + interests + 8 search themes + mandatory negative list, documented in `review/2026-07-06_students_resume_setup.md`. That's the version that's converting. Copy that spec forward into Aug rather than these placeholders — do not treat this section as current.

## Landing
- **URL:** ~~https://anrak.legal/feed~~ → **https://anrak.legal/chat**
- **CORRECTED 2026-07-12:** `/feed` is the content-first page that produced 1,723 clicks / 0 conversions in Campaign 02 ([[F-01]] — confirmed dead funnel). Students PMax was deliberately resumed onto `/chat` instead on 2026-07-06, which has a live soft gate (1 free prompt, then a "Sign in to continue" wall routing to `/onboarding`) — that's the funnel actually producing the 29 conversions above ([[F-03]]). This brief pointed at `/feed` from its original 07-02 draft and was never corrected before now. `config.yaml`'s `landing_page` field for Students had the same drift — fixed in this session too.

## Creative
- **Available:** 3 images, 1 YouTube video, 8 headlines
- **NOTE 2026-07-12:** stale — the live asset group was overhauled 2026-07-06 (10 `pmax_set` images + 1 custom hero video, junk/reject assets removed; 5 Google auto-generated videos remain but can't be deleted). Pull current counts from `api.get_creatives()` before finalizing this section, don't reuse these numbers.

## Context
- **Previous learnings:** 99% mobile, content-first funnel needs CTA, no audience signals last time
- **Confirmed since (2026-07-06→11):** /chat + fixed conversion tracking + audience signals together produced this account's first-ever conversions — 29 signups, ₹4,387 spend, cumulative CPA ₹151.29, CVR 4.6%. Bidding phase gate has been crossed: Students is now in **GROWTH** phase (29/30 conversions in the rolling 30-day window, one away from Optimization / Target CPA eligibility). The three changes landed together, so don't credit any single one alone — see [[C-06]].
- **Hard constraints:** No direct /signup landing, budget max 1000/day

## Pre-launch blockers — must resolve before council review
1. **[[T-05]] Conversion goal contamination.** Students currently inherits the account-default conversion goals, which includes both SIGNUP and CONTACT (the lawyer goal) as biddable — Maximize Conversions is technically allowed to chase a lawyer contact on the Students campaign. Not fixed yet on the live Jun campaign (deliberately — didn't want to risk restarting an already-converting learning phase). **This Aug rebuild is the designated fix point.** Set campaign-specific conversion goals = SIGNUP only for the Students campaign, and (mirror-image) = CONTACT only for the Lawyers campaign, before either goes live.
2. **Lawyers has no creative.** The 70/30 split in this brief assumes Lawyers launches alongside Students on 2026-08-01. As of 2026-07-12, Lawyers PMax is still HELD — beacon is verified live, but no dedicated Lawyer creative set has been built. Either build Lawyer creative before Aug 1, or launch Students-only on the original schedule and hold Lawyers' 30% (₹4,200) until creative is ready — don't launch Lawyers on stale/reused Students creative just to hit the date.
3. **Deprecated tag cleanup still owed.** `AW-17593778001` is still loading in prod (viewthrough/remarketing pings only, no conversion double-count risk, but it's polluting remarketing audiences). Not a launch blocker, but flag to operator — the `layout.tsx` removal diff has been owed since 2026-07-06.

---
## LLM Council Review
_This section is filled by the 4-layer council. Do not edit manually._

**Status:** PENDING COUNCIL REVIEW — brief corrected 2026-07-12, ready for council once the operator confirms the 3 pre-launch blockers above have a plan.

Once this brief is complete, open Claude Code and run:
```
/ads-council
```
The council will review this brief, flag inconsistencies, and produce a GO / NO-GO verdict before any campaign is created.
