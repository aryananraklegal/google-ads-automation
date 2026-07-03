# INTERVIEW.md — Campaign Brief Questionnaire

> Addy runs this before every new campaign. One question at a time.
> Output: a completed CAMPAIGN_BRIEF.md.
> Do not proceed to COUNCIL.md until every required field is answered.

---

## Required fields (Addy asks these in order, waits for each answer)

**1. Campaign name**
"What should we call this campaign? I'll use the format [Type]-[Audience]-[MonthYear] — e.g. PMax-Students-Jul2026. Does that work or do you want something different?"

**2. Audience**
"Who are we targeting — Students, Lawyers, or both in separate campaigns?"

**3. Daily budget**
"What's the daily budget in INR? I'll flag if it's below the minimum I'd recommend for the learning phase."

**4. Flight dates**
"When do we launch, and is there an end date or are we running open-ended?"

**5. Landing page**
"Where do we send clicks? For students we've been using /feed. For lawyers, /. Is that still right, or are we testing something new?"

**6. Conversion goal**
"What counts as a conversion for this campaign? Student signup on /onboarding, lawyer contact form, or something else?"

**7. Creatives**
"Do we have fresh creatives ready — images, headlines, descriptions? Or are we reusing assets from the last campaign?"

**8. Audience signals**
"Do we have a customer list ready to upload as audience signal? This is a Phase 0 blocker for PMax."

**9. Search themes**
"Do we have 10–15 seed keywords to set as search themes? Also a Phase 0 blocker."

**10. Budget rationale**
"Quick gut check — why this budget? Is it based on a target CPA, a monthly cap, or available spend?"

---

## Output — CAMPAIGN_BRIEF.md

Once all questions are answered, Addy writes CAMPAIGN_BRIEF.md:

```md
# CAMPAIGN_BRIEF.md

**Created:** YYYY-MM-DD
**Status:** PENDING COUNCIL REVIEW

## Campaign
- Name: [name]
- Type: Performance Max
- Audience: [audience]
- Daily budget: [amount] INR
- Flight: [start] → [end or open-ended]

## Funnel
- Landing page: [url]
- Conversion goal: [goal]
- Conversion action: [resource name from config.yaml]

## Creatives
- Images: [ready / reusing Campaign_XX / to be sourced]
- Headlines: [ready / count]
- Descriptions: [ready / count]

## Targeting
- Audience signal: [customer list name or "NOT READY"]
- Search themes: [list or "NOT READY"]

## Phase 0 Blockers
- [ ] Conversion tracking verified in prod
- [ ] Conversion action status = ENABLED (api.get_conversion_actions())
- [ ] Customer list uploaded
- [ ] Search themes set
- [ ] All creatives approved
- [ ] Landing page mobile load <3s

## Budget rationale
[Operator's answer]
```

Once written, Addy says: "Brief is ready. Running it through council — give me a moment."
Then proceeds to COUNCIL.md automatically.
