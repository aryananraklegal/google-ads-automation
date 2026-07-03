# CAMPAIGN.md — How to Build and Launch a Campaign

> Follow this exactly. Every step must be confirmed before the next.
> Zero shortcuts. A missed step = wasted spend.

---

## Phase 0 — Blockers (must all be ✅ before any campaign goes live)

- [ ] Conversion tracking verified in prod (DevTools network tab — beacon fires on `/onboarding` page load)
- [ ] Conversion action status = ENABLED in Google Ads UI (`api.get_conversion_actions()`)
- [ ] Landing page loads on mobile in <3s (test on real device, not desktop emulator)
- [ ] Negative keyword list attached to campaign
- [ ] Customer list audience uploaded (for audience signals)
- [ ] All creatives approved — no disapproved assets
- [ ] Budget confirmed by Kapil

Do not proceed to Phase 1 until all boxes are checked. State each one explicitly.

---

## Phase 1 — Brief

Run `INTERVIEW.md` questionnaire. Output: `CAMPAIGN_BRIEF.md`

Minimum required fields:
- Campaign name (naming convention: `[Type]-[Audience]-[MonthYear]`)
- Audience (Students / Lawyers / Both)
- Daily budget (INR)
- Flight dates (start → end or open-ended)
- Landing page URL
- Goal: what counts as a conversion
- Creatives available (images, headlines, descriptions, videos)

---

## Phase 2 — Council Review

Run `/ads-council` on the CAMPAIGN_BRIEF.md.
Must get GO or GO WITH CONDITIONS before Phase 3.
No confirmation code = no build.

---

## Phase 3 — Build

Using `campaigns/Campaign_02_Jun2026/secrets/build_campaigns.py` as reference template:

1. Update `CREATIVES` path to point to new campaign's creatives folder
2. Update campaign resource names if creating new campaigns
3. Run validation checks before executing:
   - `check_headlines.py` — character count validation
   - `check_aw_ids.py` — verify asset IDs resolve
4. Run build script with confirmation code logged

**Idempotency check:** Before any create operation, query to confirm the entity doesn't already exist.

---

## Phase 4 — Launch Checklist

- [ ] All assets uploaded and showing "Pending" or "Eligible" (not "Disapproved")
- [ ] Campaign status = ENABLED
- [ ] Budget live (check spend within 2 hours of launch)
- [ ] Conversion tracking test: sign up in incognito → confirm beacon in DevTools
- [ ] Log launch in CONTEXT.md under Outcomes

---

## Phase 5 — Day 3 Check

Run DAILY.md routine. If 0 conversions with >50 clicks — do NOT wait. Immediately:
1. Run `api.get_search_terms()` — what queries is Google sending?
2. Check landing page on mobile — is the CTA visible above the fold?
3. If both look fine — wait until day 5 before action.
4. If queries are off-brand — add negatives (council required).
