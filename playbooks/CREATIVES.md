# CREATIVES.md — Addy's Visual Creation Playbook

> **Rule #1 — Zero inferences on creative direction.**
> Addy never recommends an image style, copy angle, or visual format from training knowledge.
> Every creative session starts with live research. No exceptions.

---

## Step 0 — Load creative memory (always first)

Before anything else, read `CREATIVE_BELIEFS.md`.

This file holds what's been learned across all previous creative sessions — prompt patterns that work, formats that got Best labels, CTAs that council approved, competitor visual patterns already researched. Reading it means we don't repeat mistakes or redo research we've already done.

If `CREATIVE_BELIEFS.md` doesn't exist yet: copy `CREATIVE_BELIEFS.md.example` to `CREATIVE_BELIEFS.md` and proceed. Addy will populate it over the first few sessions.

---

## When to use this playbook

- User asks Addy to help create or brief images/videos for a campaign
- User asks what kind of creatives to run
- Addy is reviewing asset performance labels (Low/Good/Best) and wants to recommend changes
- Starting a new campaign that needs a fresh creative brief

---

## Step 1 — Pull own creative performance first

Before any research, check what's already working in this account:

```python
api.get_creatives(start, end)
```

Read the output. Note:
- Which asset groups have "Best" or "Good" labels
- Which have "Low" labels — these need replacing
- What image types, headlines, and descriptions are tagging well
- How long the current assets have been running

**This is the baseline.** Don't recommend replacing anything rated Good or Best unless there's a specific reason.

---

## Step 2 — Live competitor research (mandatory, no skipping)

**Use the browser tool. Navigate to:**

```
https://adstransparency.google.com/
```

Search for competitors and adjacent players in Indian legal tech. Suggested searches (adapt based on campaign audience):

**For student/junior lawyer campaigns:**
- `legal research India`
- `AI legal assistant`
- `legal drafting tool`
- `law firm software India`

**For lawyer/firm campaigns:**
- `legal practice management`
- `contract drafting AI`
- `legal AI India`
- `case management software lawyers`

**For each search, note:**
- What visual formats are being used (illustration vs photo vs text-heavy)
- Colour palettes dominating the space
- Headline angles — fear-based, benefit-based, social proof, feature-led
- What CTAs appear most ("Try free", "Book demo", "Start today")
- Any formats that look high-effort / high-production

**Screenshot or describe findings in session log.** Do not proceed to Step 3 without completing at least 3 searches.

> If the browser tool is unavailable this session: explicitly tell Kapil — "I can't access the Transparency Centre right now so I'm skipping competitive research. The brief I give you will be based on account data only, not live market intel. You may want to check manually before we finalise."

---

## Step 3 — Interview the user (or recommend based on research)

Ask Kapil these questions before writing any creative brief. Skip questions he's already answered.

**Q1. Who is this creative for?**
Students / Junior lawyers / Senior lawyers / Law firms / All

**Q2. What's the one thing this image needs to communicate?**
(Don't accept "make it look good" — push for a specific message or feeling)

**Q3. Do we have real assets to work with?**
- Product screenshots (which screen/feature?)
- Team/office photos
- Existing brand visuals (logo, colour palette)
- Or starting from scratch?

**Q4. What's the CTA?**
Sign up / Book a demo / Try free / Learn more / Other

**Q5. Any visual direction preference?**
- Clean/minimal tech aesthetic
- Bold/confident B2B
- Warm/human (people using the product)
- Text-heavy (strong headline, image secondary)
- No preference (Addy recommends)

If Kapil says "no preference" on Q5 — use Transparency Centre findings from Step 2 to recommend the direction that is underused by competitors (opportunity gap) OR the direction that dominant performers are using (proven format). State which one you're doing and why.

---

## Step 4 — Write the creative brief

Once research and interview are complete, output a brief in this format:

---

### Creative Brief — [Campaign Name] — [Date]

**Audience:** [from Q1]
**Core message:** [from Q2]
**CTA:** [from Q4]
**Visual direction:** [from Q5 or Addy's recommendation]
**Insight source:** [what from Transparency Centre informed this]

#### Image assets required (PMax specs)

| Format | Dimensions | Quantity | Notes |
|---|---|---|---|
| Landscape | 1200×628px | 3–5 | Primary display format |
| Square | 1200×1200px | 3–5 | YouTube + mobile |
| Portrait | 960×1200px | 2–3 | Stories / vertical placements |
| Logo (landscape) | 1200×300px | 1 | Must be on white/transparent bg |
| Logo (square) | 1200×1200px | 1 | Must be on white/transparent bg |

> Max file size: 5120KB per image. Accepted formats: JPG, PNG, GIF (static only for PMax).
> Text overlay must be ≤20% of image area — Google rejects heavy-text images.

#### Headlines (short) — 30 chars max, need 5
1. [draft]
2. [draft]
3. [draft]
4. [draft]
5. [draft]

#### Headlines (long) — 90 chars max, need 5
1. [draft]
2. [draft]
3. [draft]
4. [draft]
5. [draft]

#### Descriptions — 90 chars max, need 5
1. [draft]
2. [draft]
3. [draft]
4. [draft]
5. [draft]

#### Art direction notes
- [specific visual direction: colours, tone, imagery style]
- [what to avoid based on competitor research]
- [any brand constraints]
- [which existing assets to repurpose if any]

---

## Step 5 — Tool recommendation (Addy does not generate images)

Addy briefs. She does not generate. After delivering the brief, tell Kapil which tool fits:

| Need | Recommended tool |
|---|---|
| Quick social-style graphics | Canva (MCP connected — Addy can create directly) |
| AI-generated product visuals | Higgsfield (MCP connected — Addy can generate) |
| Brand-consistent professional | Canva with brand kit |
| Photography-style images | Higgsfield generate_image |
| Animated/video assets | Higgsfield generate_video |

If Kapil wants Addy to generate directly using the connected MCP tools, she can — but she always shows the brief first and gets a "yes" before generating anything.

---

## Step 6 — After assets are created

Once Kapil has the final images:

1. Save generated images to `visuals/generated/[campaign-label]/` using this naming convention:
   `YYYY-MM-DD_[campaign-label]_[format]_v[N].png`
   Example: `2026-08-01_PMax-Students_landscape_v1.png`
2. Save Transparency Centre browser screenshots to `visuals/screenshots/`:
   `YYYY-MM-DD_[search-term].png`
3. Upload to Google Ads asset group via UI (Addy cannot upload images via API — Google Ads API does not support image upload for PMax asset groups)
4. Addy logs the asset names, upload date, and brief summary in `review/YYYY-MM-DD_creatives.md`
5. Schedule a check-in: pull `api.get_creatives()` after 14 days to see if labels have assigned
6. If any asset comes back "Low" within 30 days — flag it and run this playbook again for replacement

---

## Step 7 — Update CREATIVE_BELIEFS.md

At the end of every creative session, ask the 5 update questions in CREATIVE_BELIEFS.md:
- Higgsfield prompt worked or flopped?
- Asset labels assigned since last session?
- Council vetoed a copy angle or CTA?
- Transparency Centre research revealed a visual pattern?
- A brand constraint caused a production problem?

Revise beliefs in place. Add new ones with the next CR-ID. Write nothing if no evidence changed.

---

## What Addy never does in creative sessions

- Never recommends a visual style from training knowledge without citing live Transparency Centre evidence
- Never skips Step 2 without explicitly telling Kapil she's skipping and why
- Never generates images without showing the brief first
- Never uploads images to Google Ads (not supported via API — always manual)
- Never calls a creative "good" based on aesthetics — only on data (asset labels, CTR by asset)
