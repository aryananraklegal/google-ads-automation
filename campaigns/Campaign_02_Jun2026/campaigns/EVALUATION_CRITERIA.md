# Campaign 02 — Evaluation Criteria & LLM Council Findings
**Date:** 2026-06-24
**Council:** 4 independent Opus critics (PPC strategy / India market / Conversion tech / Ad copy)
**Protocol:** Adversarial — each critic tasked to break the spec, not validate it

---

## PRE-LAUNCH GATE: All CRITICAL items must be resolved before API build

---

## DIMENSION 1 — PPC Strategy (Critic: Senior PPC Strategist)

### CRITICAL
**C1. Asset groups: 3 per campaign is structurally wrong at this budget**
- ₹786/day students split across 3 groups = ~₹262/group/day. Google won't meaningfully explore 3 groups at that spend. Budget gets fragmented before the algorithm can learn anything.
- Fix: **1 asset group per campaign at launch.** Merge best headlines/descriptions from all 3 groups into 1. Add more groups only after 50+ conversions.

**C2. Lawyer budget (₹3,000 / ₹214/day) is below viable PMax serving threshold**
- At ₹400-600 CPA you get 0.36-0.54 conversions/day. PMax needs volume to learn. This campaign will under-deliver and never exit learning in 14 days.
- Math check: 7 lawyers × ₹600 CPA = ₹4,200. Budget is ₹3,000. Target and budget are mutually inconsistent.
- Fix: Either (a) increase lawyer budget to ₹5,000+ by reallocating from students, or (b) accept max 5 lawyer conversions and set expectation accordingly.

### HIGH
**H1. 3-phase bidding causes 2 learning resets inside a 14-day campaign**
- Setting tCPA on day 6 resets learning. Tightening on day 11 resets it again. With a short flight you spend most of the budget in learning and never reach steady state.
- Fix: **Run Maximize Conversions for the full 14 days on both campaigns.** Do not touch bid strategy mid-flight. Only consider tCPA on students if they exceed 50 conversions in first 7 days (unlikely).

**H2. 150+ conversion target is the optimistic ceiling, not the plan**
- At mid-CPA (₹80 students / ₹500 lawyers) + 20-30% learning-phase tax: realistic outcome is 100-120 total, not 150+.
- Fix: Update internal target to 100-120 realistic / 150 stretch. Do not set tCPA off 5-day data.

### MEDIUM
**M1. Launching without display creatives lets Google auto-generate low-quality video**
- PMax will stitch images into auto-gen video — off-brand for a legal AI product.
- Fix: Ship Higgsfield images within days 1-3. At minimum 1 landscape (1200×628) + 1 square (1200×1200) per campaign.

**M2. Shared negative list attachment on PMax must be verified**
- Account-level negative lists historically had limited/inconsistent PMax application.
- Fix: After campaign creation, confirm in UI that sharedSets/12128615235 appears under each PMax campaign's negative keywords tab.

### EVALUATION METRICS (PPC dimension)
| Metric | Green | Yellow | Red — Action |
|---|---|---|---|
| Day 1-3 impressions | >500/day | 100-500 | <100 = asset or targeting issue |
| Day 3 conversions | >5 | 1-4 | 0 = verify tracking before touching bids |
| Day 7 CPA students | <₹150 | ₹150-300 | >₹300 = pause + diagnose |
| Day 7 CPA lawyers | <₹600 | ₹600-900 | >₹900 = pause lawyer campaign |
| Budget utilization | 90-100% | 70-90% | <70% = under-delivery, check status |

---

## DIMENSION 2 — India Market Fit (Critic: India Digital Marketing Strategist)

### CRITICAL
**C3. Custom intent keywords don't match how Indian law students actually search**
- "claude for legal research" — near-zero volume. Claude has negligible brand awareness with Indian undergrads (ChatGPT is the default AI verb in India).
- Real student queries: "memorial format moot court", "moot court memorial sample", "indiankanoon alternative", "free SCC online", "IPC notes pdf", "CLAT PG preparation", "judgment summary site".
- Fix: Replace custom intent list with India-specific search patterns. New list below.

**C4. ₹11,000 student budget fights gravity — discovery is referral-driven, not auction-driven**
- Indian law students adopt tools via WhatsApp batch groups, Telegram channels, Instagram lawfluencers, Lawctopus, LawBhoomi — channels Google cannot reach.
- PMax buys the wrong moment in the funnel for this segment.
- Fix: This is a structural limitation. Mitigate by (a) using PMax as a remarketing + warm-audience tool, not cold discovery, (b) running a parallel Instagram/WhatsApp seeding campaign as the actual discovery channel.

### HIGH
**H3. "Claude + Anrak" messaging fails with Indian students who don't know Claude**
- "Claude + Anrak = Legal AI" reads as "[unknown] + [unknown] = [category]" to most Indian law students. Anchors against ChatGPT (the known free alternative) without answering "why not ChatGPT?"
- Fix: Replace with India-specific outcome framing. "Bare Acts, Judgments, Memorials — One Platform" beats "Claude + Anrak" with this audience.

**H4. Lawyer messaging is aimed at the wrong seniority level**
- Senior advocates bill by appearance and delegate drafting to juniors. "Cut drafting time by 60%" is a junior's pain, not the economic buyer's.
- Indian advocates' actual objections: AI hallucination risk, confidentiality, citation accuracy. Price is not the objection.
- Fix: Reframe lawyer copy around accuracy + confidentiality + peer proof, not speed + price.

**H5. ChatGPT is the unpriced default — none of the copy counters it**
- Every ad implicitly competes with "why not just use ChatGPT free?" No headline addresses this.
- Fix: Add India-specific differentiation headlines: "ChatGPT Doesn't Know Indian Case Law", "Indian Courts. Indian Statutes. Not Generic AI."

### REVISED CUSTOM INTENT KEYWORDS (replace existing list)
**Students:**
- moot court memorial format, moot court memorial sample india, how to prepare moot court, moot court problem research, supreme court judgment research, high court judgment search free, indiankanoon case search, bare act notes llb, law project help ai, legal research ai india, ai for law students, legal drafting ai free

**Lawyers:**
- legal drafting software india, contract drafting ai india, legal research tool india, ai for advocates india, high court judgment search, legal document automation india, law firm management software india, nda drafting tool india

### EVALUATION METRICS (India market dimension)
| Signal | Green | Yellow | Red |
|---|---|---|---|
| Student CTR | >4% | 2-4% | <2% = copy not resonating |
| Search terms showing in report | India-specific legal intent | Mixed | Irrelevant / competitor navigation |
| Bounce rate proxy (session depth) | >2 pages | 1-2 | 1 page = landing page mismatch |
| Lawyer conversion form completion | Form started + submitted | Form started only | No form starts |

---

## DIMENSION 3 — Conversion Tracking & Technical (Critic: CRO / Analytics Expert)

### HIGH (need dev fixes before or immediately after launch)

**H6. event_callback redirect has no timeout or gtag-absent fallback (Fix 3)**
- If gtag.js is blocked (ad blockers, Jio DNS blocking) or times out on a slow Indian mobile connection, event_callback never fires and the user is stranded on the form — no redirect.
- Fix (dev, pre-launch): Add (a) event_timeout: 2000, (b) a "already-redirected" boolean guard, (c) a fallback router.push if gtag or window.dataLayer is undefined. User must never be blocked by the pixel.

**H7. Lawyer conversion fires on any direct URL load or refresh (Fix 4)**
- /contact-thank-you is reachable directly. ConversionFire.tsx useEffect fires on every mount, including bookmarks, refreshes, and bot crawls.
- Fix (dev, pre-launch): Gate fire behind a submit-issued token (sessionStorage flag set at form submit, consumed once on thank-you page load). Clear after firing.

**H8. 5 enabled codeless conversion actions still set to "Include in Conversions"**
- "Submit lead form", "B2B Enterprise Lead Submit (1)", "B2B Lead - Thank You Page" are ENABLED and likely still primary. Google Smart Bidding optimizes toward all primary conversions — these noisy codeless actions corrupt the signal.
- Fix (Google Ads UI, pre-launch): Set all conversion actions EXCEPT 7660090544 and 7660090547 to "Include in Conversions = No". Also disable auto-tracking "Submit lead form" in Google tag settings.

**H9. Enhanced conversions flag is set but no hashed data passed — feature is OFF**
- allow_enhanced_conversions: true without user_data in the conversion event = nothing enhanced. ~5-8% attribution forfeited on Indian Chrome/Android traffic.
- Fix (dev, post-launch acceptable): SHA-256 hash the normalized email at form submit and pass user_data: { sha256_email_address: hashedEmail } in the gtag conversion call.

### MEDIUM
**M3. DPDP: allow_ad_personalization_signals unconditional**
- Personalization signal sharing for all Indian visitors with no consent capture. Legal exposure for a legal-services company specifically.
- Fix (dev, post-launch): Implement Google Consent Mode v2 in default-denied state. Gate ad_user_data / ad_personalization behind explicit DPDP consent banner.

### EVALUATION METRICS (Technical dimension)
| Check | Pass | Fail — Action |
|---|---|---|
| DevTools: student signup fires label cqpwCLDpzsQcEKCi4v1C | Hits googleads.googleapis.com | No hit = tracking broken |
| DevTools: /contact-thank-you fires label pCMiCLPpzsQcEKCi4v1C | Hits on fresh load | No hit = ConversionFire not mounted |
| Conversion appears in Google Ads UI within 3h of test | Conversion recorded | 0 = check "Include in Conversions" |
| Redirect happens even with no network (airplane mode test) | User moves to next step | User stranded = no fallback |
| Direct URL load /contact-thank-you does NOT record conversion | No hit | Hit = gating broken |

---

## DIMENSION 4 — Ad Copy & Compliance (Critic: Direct Response Copywriter)

### CRITICAL
**C5. "Claude" trademark: 3+ headlines use co-brand/equation framing without authorization**
- "Claude + Anrak = Legal AI", "Anrak Adds Indian Law to Claude AI", "Already Using Claude for Law?", "One Click Claude Install", "Add Anrak to Claude Now" — five headlines across student + lawyer groups use Anthropic's trademark in co-brand framing.
- Risk: Google trademark disapproval (account strike risk) + Anthropic complaint = ad removal mid-flight.
- Fix: Must confirm Anthropic ToS permits this OR rewrite. Safe fallback: "Works With Your AI Assistant", "Plug Into Your Existing AI Workflow".

**C6. "Beat Every Opposing Counsel" — BCI Rule 36 + absolute claim**
- Bar Council of India Rule 36 prohibits advocates from advertising superior results. While Anrak is a vendor not an advocate, the ad is aimed at law students and makes an absolute performance guarantee.
- Google policy: "every" = absolute = disapproval-prone.
- Fix: Replace with "Build Stronger Moot Arguments" or "Win More Moots with Better Research".

### HIGH
**H10. "Indian Advocates Cut Drafting Time by 60%" requires substantiation**
- Specific quantified claim (60%) requires a documented, on-page source visible on the landing page. No dataset = Consumer Protection Act 2019 / CCPA misleading advertisement exposure.
- Fix: Either (a) produce real data and cite it on the landing page, or (b) change to "Cut Drafting Time Dramatically" / "Draft Faster with AI".

**H11. "Law School's Best AI Tool" — superlative requiring third-party verification**
- Google requires third-party proof visible on landing page for "best" claims.
- Fix: Change to "A Law School Favourite" or "Top-Rated by Law Students".

**H12. Free / Rs.499 signal bleed across asset groups**
- Student groups have "Free for Law Students" / "No Credit Card" while lawyer groups have "Plans from Rs.499/month". PMax mixes headlines — a lawyer seeing "No Credit Card. Free Signup" loses trust in the paid product.
- Fix: Strict separation. No "free" framing in lawyer asset group. No pricing framing in student asset group.

**H13. Student Group 1 (Claude Wave) is the weakest group — rewrite before launch**
- Entire angle depends on Claude brand awareness (negligible in Indian students) and co-brand authorization (pending).
- Fix: Rebuild Group 1 around India-specific outcomes. New angles: "All Indian Courts. One Search.", "Bare Acts + Judgments + AI. Free.", "Research What Takes Hours in 30 Seconds."

### EVALUATION METRICS (Copy dimension)
| Signal | Green | Yellow | Red |
|---|---|---|---|
| Asset group label (day 5) | Good / Best | Learning | Low = swap headlines |
| Headline combination report | Logical combos served | Some weak combos | Brand incoherence = restructure |
| Ad disapprovals | 0 | 1-2 minor | Any trademark disapproval = pause + rewrite |
| CTR by asset group | Best group >4% | 2-4% | <2% = copy failing |

---

## GO / NO-GO GATE

### Must be GREEN before Claude builds campaigns via API:

| # | Item | Owner | Status |
|---|---|---|---|
| C1 | Collapse to 1 asset group per campaign | Claude (spec rewrite) | PENDING |
| C2 | Lawyer budget math reconciled | Decision needed | PENDING |
| C3 | Custom intent keywords replaced with India-specific list | Claude (spec rewrite) | PENDING |
| C5 | "Claude" trademark headlines: authorization confirmed OR replaced | Founder / Copy rewrite | PENDING |
| C6 | "Beat Every Opposing Counsel" removed | Claude (copy rewrite) | PENDING |
| H1 | Bidding: Maximize Conversions for full 14 days, no mid-flight changes | Claude (spec update) | PENDING |
| H6 | event_callback timeout + fallback redirect | Dev | PENDING |
| H7 | Lawyer conversion gated behind submit token | Dev | PENDING |
| H8 | Codeless conversion actions demoted to non-primary in UI | Manual in Google Ads UI | PENDING |
| H10 | "by 60%" removed or substantiated | Copy rewrite | PENDING |
| H11 | "Law School's Best AI Tool" softened | Copy rewrite | PENDING |
| H12 | Free / Rs.499 bleed eliminated | Copy rewrite | PENDING |

### Can launch WITH but must fix within 72h:
- H9: Enhanced conversions hashed email (dev)
- M1: Higgsfield display creatives
- M3: DPDP consent mode (dev)
- M2: Verify shared negative list shows in PMax campaign UI

---

## POST-LAUNCH DAILY CHECK (Claude runs via API each morning)

```
Day 3:  0 conversions → verify DevTools before touching anything
Day 5:  Pull asset group labels → pause any "Low" groups
Day 7:  Pull search terms → add any irrelevant terms to negative list
Day 7:  CPA check → if students <₹150, on track; if >₹300, pause + diagnose
Day 10: Pull device split → if mobile CPA >2x desktop, consider bid adjustment
Day 14: Full audit → compare actuals vs projections, document for Campaign 03
```
