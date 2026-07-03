# BELIEFS.md — Addy's Standing Knowledge

> **What this file is:** Compressed, weighted beliefs derived from campaign outcomes and decisions.
> Not a log. Not a transcript. A living model of what Addy knows to be true about this account.
>
> **How it works:**
> - Addy reads this at every session start alongside CONTEXT.md
> - CONTEXT.md = what happened | BELIEFS.md = what it means
> - At session end, Addy asks: "Did anything this session change a standing belief?"
>   - If yes → update the relevant belief (revise the statement, update confidence, update evidence)
>   - If no new evidence → leave unchanged
> - Beliefs are never deleted — they are revised or marked [SUPERSEDED BY: belief-name]
>
> **Confidence levels:**
> - CONFIRMED — seen across 2+ campaigns or explicitly verified
> - LIKELY — one strong signal, no contradicting evidence
> - HYPOTHESIS — untested, derived from reasoning not data
> - SUPERSEDED — belief was wrong or outdated, replaced
>
> **Format per belief:**
> ```
> ### [BELIEF-ID] Short belief statement
> Confidence: LEVEL | Last updated: YYYY-MM-DD | Evidence: [source]
> Detail: one or two sentences of context
> ```

---

## Audience

### [A-01] This account's traffic is almost entirely mobile
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: Campaign 01 + Campaign 02 device reports
Detail: 99.8% mobile observed across both PMax campaigns (Jun 2026). All creatives, landing pages, and CTAs must be designed for mobile first. Desktop performance is negligible.

### [A-02] Students and lawyers have different conversion behaviours
Confidence: LIKELY | Last updated: 2026-07-03 | Evidence: Campaign 02 outcomes + funnel analysis
Detail: Students land on content (/feed) and browse without converting. Lawyers are lower volume but higher intent — they look for demos or contact forms. Requires separate landing strategies, not a one-size approach.

### [A-03] The 18–24 age bracket produces low-quality traffic
Confidence: LIKELY | Last updated: 2026-07-03 | Evidence: Demographic exclusion decision in Campaign 02
Detail: Excluded from both campaigns. Not yet tested whether re-including them would hurt or help — exclusion is a standing rule until tested.

---

## Funnel

### [F-01] Content-first landing on /feed produces zero direct signups
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: Campaign 02 — 1,723 clicks, 0 conversions, landing: /feed
Detail: Users land, read, and leave. No CTA or gate drives signup. Changing the landing page or adding a sticky CTA is the single highest-leverage funnel fix available.

### [F-02] The onboarding form has high friction on mobile
Confidence: LIKELY | Last updated: 2026-07-03 | Evidence: 7 required fields including multi-select on mobile
Detail: Practice area multi-select and role-specific fields on a mobile screen are a known drop-off risk. Not yet tested — hypothesis that making practice areas optional would improve completion rate.

### [F-03] /chat is public — removes signup urgency
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: Product review + codebase check
Detail: Unauthenticated users can use /chat without creating an account. This removes the primary reason to sign up during a session. A soft gate (2–3 messages before prompt) is the recommended fix but untested.

### [F-04] Google OAuth users bypass /onboarding and need a modal fallback
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: PR #84 — OnboardingCheck component analysis
Detail: OAuth users go /auth/callback → /chat, skipping /onboarding entirely. OnboardingCheck modal handles this. Conversion event now fires via onSuccess callback on modal submit (PR #84, pending merge).

---

## Conversion Tracking

### [T-01] Conversion tracking was broken for all of Campaign 01 and Campaign 02
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: 2,282 clicks + 0 conversions across both campaigns
Detail: The conversion event fired too deep in the funnel (onboarding form submit) which most users never reached. Root cause: content-first funnel + public /chat page = users never get to the form.

### [T-02] Conversion event now fires on /onboarding page load
Confidence: LIKELY | Last updated: 2026-07-03 | Evidence: PR #84 (pending merge — not yet confirmed in prod)
Detail: SignupConversionFire.tsx fires on page load with transaction_id: user.id. Server-side guard ensures only genuine new users reach /onboarding. Must be verified in prod via DevTools network tab before campaigns resume. Update to CONFIRMED once verified.

### [T-03] Tag AW-17980494112 is the only active conversion tag
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: Google Ads UI verification + layout.tsx audit
Detail: Deprecated tag AW-17593778001 was removed from layout.tsx in PR #84. All conversions route through AW-17980494112 only.

### [T-04] Google deduplicates conversions per click via Count = One setting
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: Google Ads conversion action settings
Detail: Even if the beacon fires twice, Google counts one conversion per click. transaction_id: user.id adds a second deduplication layer client-side.

---

## Campaign Performance

### [C-01] PMax CPCs in this account are display/YouTube range, not search range
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: Campaign 02 — Students ₹1.01 CPC, Lawyers ₹1.42 CPC
Detail: These are consistent with display/YouTube inventory, not search. PMax without audience signals defaults to broad low-intent inventory. Adding customer list signals is expected to shift distribution toward higher-intent placements.

### [C-02] PMax without audience signals produces broad, low-intent traffic
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: Campaign 02 — 2,282 clicks, 0 conversions, no signals set
Detail: Algorithm flew blind in Campaign 02. Customer list upload and search themes are required before Campaign 03 launches. Both are Phase 0 blockers.

### [C-03] 0 conversions is not sufficient to trigger kill rule during PMax cold-start
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: PMax learning phase research + Campaign 02 analysis
Detail: PMax needs minimum 14 days AND ₹3,000 (students) / ₹5,000 (lawyers) spend before kill rule evaluation. Killing earlier destroys the learning phase. Campaign 02 would have been killed incorrectly under the old 3× CPA rule.

### [C-04] Campaign 01 (Search) and Campaign 02 (PMax) both produced 0 conversions
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: CONTEXT.md Outcomes
Detail: Campaign 01: ₹6,273 spend, 162 clicks, 0 conv. Campaign 02: ₹2,535 total spend, 2,282 clicks, 0 conv. Both pre-date the tracking fix. Campaign 03 will be the first campaign with correct tracking in place.

---

## Account Operations

### [O-01] Manager account ID 7438563825 causes auth failure
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: Repeated auth failures during setup
Detail: Always use sub-account ID 2183727993. The manager account ID is permanently excluded from config.yaml and validate_config.py blocks it explicitly.

### [O-02] The 70/20/10 budget allocation rule applies to all campaign decisions
Confidence: CONFIRMED | Last updated: 2026-07-03 | Evidence: Explicit operator decision
Detail: 70% to proven performers, 20% to scaling, 10% to experiments. No campaign gets funded outside this framework without explicit operator override.

### [O-03] Ad schedule Mon–Fri 9AM–6PM IST is assumed correct for B2B
Confidence: HYPOTHESIS | Last updated: 2026-07-03 | Evidence: Assumption — not validated by impression share data
Detail: Never tested whether weekend or evening traffic converts differently. Validate with actual impression share by day/hour once Campaign 03 produces conversion data.
