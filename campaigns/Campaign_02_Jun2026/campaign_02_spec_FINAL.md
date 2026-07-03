# Anrak Legal — Campaign 02 Final Spec
**Type:** Performance Max (PMax) — both campaigns, day 1, full send
**Budget:** ₹14,000 (Google Ads free credits)
**Split:** ₹11,000 students / ₹3,000 lawyers
**Primary Goal:** Conversions only — student signups (/onboarding) + lawyer contact fills (/contact-thank-you)
**Conversion target:** 150+ total (125-162 realistic range, 150 is the stretch goal)
**Projected CPA:** ₹70-90 students / ₹400-600 lawyers
**Projected conversions:** Students 120-155 / Lawyers 5-7
**Bidding phase 1 (day 1-5):** Maximize Conversions, NO Target CPA — let Google find conversions at any price
**Bidding phase 2 (day 6-10):** Set Target CPA at observed CPA from phase 1 data
**Bidding phase 3 (day 11-14):** Tighten Target CPA 10-15% below observed — squeeze efficiency
**CPA cap on day 1:** REJECTED — starves cold PMax of volume, kills conversion count
**Learning burn:** Accepted. We spend to get conversions, not to avoid learning phase costs.
**API Control:** Live via Claude Code (customers/2183727993)
**Last updated:** 2026-06-24

---

## CHANGELOG (decisions made in session)

| Decision | Detail |
| Budget reallocation | Shifted to ₹11k students / ₹3k lawyers — students have lower CPA and no purchase friction |
| Conversion target | 150+ over 14 days. Floor is 80-100, stretch is 150. |
| CPA cap rejected | No Target CPA on day 1. Set it on day 6 using real observed data from phase 1. |
|---|---|
| Campaign type | PMax for both audiences — not Search. Students need visual ads, lawyers need scale. |
| Search-first hedge | Considered and rejected. Accept learning burn as long as conversions are the output. |
| Display creatives | Higgsfield generates static images. Launch with images so PMax doesn't default to Search-only. |
| No GTM | Not needed. Direct gtag.js already in codebase. Cleaner for Next.js SPA. |
| Tracking root cause found | AW-17593778001 in layout.tsx src = foreign account's tag. Must be replaced with AW-17980494112. |
| Conversion actions created via API | Student: ID 7660090544, label cqpwCLDpzsQcEKCi4v1C / Lawyer: ID 7660090547, label pCMiCLPpzsQcEKCi4v1C |
| Old student conversion label | LFUGCN34rqgcEKCi4v1C mapped to REMOVED action — caused 0 conversions in Campaign 1 |
| Conversion trigger fix | Student: must fire in form submit handler with event_callback, not page load |
| Ads Scripts for PMax | Scripts won't work — filter hardcoded to SEARCH. Automation via Claude Code API only. |
| Anthropic ToS | Must verify before launch that naming Claude in ad copy is permitted |
| Final URL expansion | Turn OFF in PMax — prevents Google sending traffic to thin/broken pages |
| Brand exclusions | Add Anrak's own brand as negative at account level — prevents PMax cannibalising organic |

---

## SECTION 1 — HARD BLOCKERS (nothing goes live until all confirmed)

### Dev fixes — 4 code changes

**Fix 1 — `app/layout.tsx` line 301: wrong account tag**
```
CHANGE: src="https://www.googletagmanager.com/gtag/js?id=AW-17593778001"
TO:     src="https://www.googletagmanager.com/gtag/js?id=AW-17980494112"
```
Why: AW-17593778001 is a foreign account's tag. All tracking was firing to the wrong place.

**Fix 2 — `app/layout.tsx`: update gtag config**
```js
gtag('config', 'AW-17980494112', {
  allow_enhanced_conversions: true,
  allow_ad_personalization_signals: true
});
```

**Fix 3 — `app/onboarding/onboarding-form.tsx` ~line 199: fix conversion label + add callback**
```js
gtag('event', 'conversion', {
  send_to: 'AW-17980494112/cqpwCLDpzsQcEKCi4v1C',
  event_callback: () => { /* move existing router.push here */ }
});
```
Why: Old label LFUGCN34rqgcEKCi4v1C mapped to a REMOVED conversion action.

**Fix 4 — Create `app/contact-thank-you/ConversionFire.tsx` and mount it**
```tsx
'use client'
import { useEffect } from 'react'

export default function ConversionFire() {
  useEffect(() => {
    if (typeof window !== 'undefined' && typeof (window as any).gtag === 'function') {
      (window as any).gtag('event', 'conversion', {
        send_to: 'AW-17980494112/pCMiCLPpzsQcEKCi4v1C'
      })
    }
  }, [])
  return null
}
```
Mount in `app/contact-thank-you/page.tsx`: `<ConversionFire />`

### Dev verification (must pass before launch)
- [ ] Chrome DevTools → Network → complete test signup → confirm hit fires to `googleads.googleapis.com` with label `cqpwCLDpzsQcEKCi4v1C`
- [ ] Same on `/contact-thank-you` with label `pCMiCLPpzsQcEKCi4v1C`

### Founder task
- [ ] Verify Anthropic brand usage policy permits naming "Claude" in third-party Google Ads copy

### Google Ads account settings (Claude does via API on launch day)
- [ ] Turn off Final URL expansion in both PMax campaigns
- [x] Shared negative keyword list created via API (38 keywords) — resource: customers/2183727993/sharedSets/12128615235
  - Competitors: maigon, casetext, legalink, harvey, vakilsearch, casemine, trilegal, law central, liquidtext, zoho legal
  - Brand: anrak legal, anrak.legal (prevent organic cannibalization)
  - Off-target: us law, uk law, lsat, bar exam, law school admission, lawyer salary
  - NOTE: attach to both PMax campaigns via CampaignSharedSetService when building via API

---

## SECTION 2 — CONVERSION ACTIONS (created via API 2026-06-24)

| Action | ID | Label | Fires on | Status |
|---|---|---|---|---|
| Student Signup - Onboarding Complete | 7660090544 | cqpwCLDpzsQcEKCi4v1C | Form submit in onboarding-form.tsx | ENABLED |
| Lawyer Contact - Thank You Page | 7660090547 | pCMiCLPpzsQcEKCi4v1C | Page load on /contact-thank-you | ENABLED |

Old removed actions (do not use): Sign-up (7516063100), B2B Enterprise Lead Submit (7635607656)

---

## SECTION 3 — CAMPAIGN ARCHITECTURE

### 2 PMax campaigns, 3 asset groups each

| Campaign | Audience | Daily Budget | Total | Landing Pages |
|---|---|---|---|---|
| PMax — Students | Law students 18-25 | ₹857/day | ₹6,000 | anrak.legal/chat, anrak.legal/feed |
| PMax — Lawyers | Practicing lawyers + new firms 25-55 | ₹1,143/day | ₹8,000 | anrak.legal, anrak.legal/chat |

### Why PMax for both
Students won't click text ads — visual-first audience, mobile-conditioned. Lawyers need reach beyond Search. Accept learning burn. Conversions are the only metric that matters.

---

## SECTION 4 — ASSET GROUPS

### PMax — Students

#### S-AG1: Claude Wave
**Headlines (15):**
Research Any Case in 30 Seconds / Free for Law Students / Claude + Anrak = Legal AI / Add Anrak to Claude Now / Your Personal AI Law Expert / India's Legal AI Platform / Moot Court? Anrak Has You / No Credit Card. Free Signup / Used by Law Students Across India / Research Faster. Draft Better. / One Click Claude Install / Built for Indian Courts / Find Any Judgment Instantly / Legal Research. Zero Effort. / Start Free Today

**Descriptions (4):**
Already using Claude for legal research? Add Anrak — one click gives Claude Indian case laws and statutes.
Free for law students. Research judgments, draft arguments, prep moot court in minutes. No credit card.
Anrak plugs into Claude and adds Indian Supreme Court, High Court judgments and drafting tools instantly.
Used by students at top law schools. No credit card. Sign up free at anrak.legal/chat.

**Audience signals:** custom intent (claude for legal research, moot court preparation, ai for law students india), interests (Law & Government, Higher Education), remarketing (520 visitors), demographics 18-28 India

#### S-AG2: Moot Court
**Headlines (15):**
Win Your Moot Court with AI / Prep Arguments in Minutes / Draft Your Memorial Instantly / Find Precedents Automatically / AI for Moot Court India / Free Moot Court Research Tool / Beat Every Opposing Counsel / Case Law at Your Fingertips / Moot Court Mode is Here / Research. Draft. Win. / Law School's Best AI Tool / Start Free. No Card Needed. / Anrak Legal for Students / AI That Knows Indian Law / Build Your Memorial with AI

**Descriptions (4):**
Anrak researches cases, drafts arguments and finds precedents for your moot court. Free for students.
Prepare your moot court memorial in half the time. Anrak knows Indian case law inside out.
Search any High Court or Supreme Court judgment instantly. Built for Indian law students.
Free for students. No credit card. Sign up at anrak.legal and start winning moot courts.

**Audience signals:** custom intent (moot court preparation india, moot court memorial drafting, how to prepare moot court arguments), demographics 18-25 India

#### S-AG3: General Legal AI for Students
**Headlines (15):**
Legal Research in 30 Seconds / AI Built for Indian Law / Free Legal AI for Students / Draft Legal Docs with AI / Find Any Judgment Instantly / Anrak: India's Legal AI / Study Smarter with AI / No More Manual Research / LLB Students Love Anrak / Research Any Statute Instantly / AI for Every Law Assignment / Start Free Today / Case Law Made Simple / India's Best Legal AI Tool / Built for Indian Courts

**Descriptions (4):**
Stop spending hours on legal research. Anrak finds judgments, statutes and arguments in seconds.
Free for LLB students. Anrak Legal knows Indian case law and helps you research and draft faster.
Research any High Court judgment, draft legal arguments and prep assignments. Free signup.
Join thousands of Indian law students using Anrak to research faster and draft smarter.

---

### PMax — Lawyers

#### L-AG1: Claude Wave
**Headlines (15):**
Indian Advocates Cut Drafting Time by 60% / Anrak Adds Indian Law to Claude AI / Already Using Claude for Law? / One Click. Full Legal AI. / Built for Indian Advocates / Research Any Judgment Now / Draft Contracts in Minutes / India's Legal AI Platform / AI That Knows Indian Law / Talk to Anrak. Get Answers. / For Practicing Advocates / Book a Free Demo Today / Legal AI for Indian Courts / Plans from Rs.499/month / Stop Doing Legal Work Manually

**Descriptions (4):**
Already using Claude for legal work? Anrak MCP adds Indian case laws, drafting and client tools in one click.
Built for Indian advocates. Anrak knows High Court judgments, Indian statutes and standard clauses.
Draft plaints, research judgments, prepare client documents — all trained on Indian law. Try free.
Book a free demo. See how advocates across India use Anrak to draft faster and research smarter.

**Audience signals:** custom intent (claude ai for lawyers, legal drafting ai india, ai for advocates india, legal research software india), interests (Legal Services, Business Productivity), remarketing (520 visitors + 200 Google-engaged), demographics 25-55 India

#### L-AG2: Legal Drafting & Research
**Headlines (15):**
Draft Any Legal Document Fast / AI Contract Drafting India / Legal Research in 30 Seconds / Stop Drafting Contracts Manually / Find Any Judgment Instantly / AI for Legal Drafting India / Review Contracts with AI / Built for Indian Advocates / High Court Judgments Instantly / Draft. Review. Win Cases. / Anrak: India's Legal AI OS / Legal AI for Law Firms / Save 3 Hours Per Case / Book a Demo Today / AI That Knows Indian Law

**Descriptions (4):**
Draft contracts, legal notices and petitions in minutes. Anrak AI is trained on Indian case law.
Research any High Court or Supreme Court judgment instantly. Built for practicing Indian advocates.
Review contracts in 2 minutes. Anrak flags missing clauses, risks and red lines automatically.
Used by advocates across India. Book a free demo and see Anrak handle your legal workflow.

#### L-AG3: New Law Firm Setup
**Headlines (15):**
Starting a Law Firm in India? / Run Your Firm on AI From Day 1 / Automate Your Legal Practice / AI for New Law Firms India / Legal OS for Indian Advocates / Cut Admin Time by 60 Percent / Research. Draft. Bill. Automate. / Built for Solo Practitioners / Law Firm Tools Powered by AI / Start Your Firm the Right Way / No More Manual Legal Work / AI Paralegal for Your Firm / Book a Free Demo Today / India's Legal Practice AI / Plans from Rs.499/month

**Descriptions (4):**
Starting a law firm? Anrak automates research, drafting, client docs from day one. Plans from ₹499/month.
Built for solo practitioners and small law firms in India. AI that handles your entire practice.
Cut your admin time by 60%. Anrak handles research, contracts, case files and client communication.
Book a free demo. See how Indian advocates use Anrak to run smarter, leaner law practices.

---

## SECTION 5 — DISPLAY CREATIVE (Higgsfield — pending generation)

### Student ad — dark theme
- Background: #0A0A0A near-black
- Bold white headline, left-aligned, large
- Grey subtext: "Free for law students. No credit card."
- Anrak product UI screenshot bottom third (dark mode)
- CTA bar: dark charcoal, "Sign Up Free →"
- Notion/Linear aesthetic, 60% empty space, 9:16 mobile

### Lawyer ad — clean corporate
- Background: #EEF2FF light blue-grey
- Dark navy headline, bold left-aligned
- White product card mockup bottom half
- CTA bar: navy, "Book a Demo →"
- Naukri FastForward layout reference, 9:16 mobile

**Status: pending Higgsfield generation. Must be ready before PMax launch.**

---

## SECTION 6 — AUTOMATION

### Claude Code (on-demand via API)
All campaign operations: create, pause, modify, report, keyword management, budget changes.
Customer ID: 2183727993 | Credentials: Campaign_02_Jun2026/secrets/google-ads.yaml

### Google Ads Scripts
NOT applicable for PMax — existing script filters AdvertisingChannelType = SEARCH.
All automation for Campaign 02 handled exclusively via Claude Code API calls.

---

## SECTION 7 — EVALUATION CRITERIA (LLM council verified 2026-06-24)

### Pre-launch checklist (all must be green)
- [ ] Fix 1-4 deployed and verified in DevTools
- [ ] Anthropic ToS confirmed for Claude naming in ads
- [ ] Higgsfield creatives generated and uploaded
- [ ] Final URL expansion OFF in both campaigns
- [ ] Account-level brand + competitor negatives added
- [ ] OAuth app status checked — not in 7-day testing token mode

### Performance benchmarks (daily check via Claude Code API)

| Metric | Green | Yellow | Red — action |
|---|---|---|---|
| Impressions day 1-3 | >500/day | 100-500 | <100 = asset issue |
| CTR | >3% | 1-3% | <1% = copy problem |
| Conversions day 1-5 | Any | 0 after day 3 | Pause + diagnose |
| Cost per conversion | <₹400 students, <₹800 lawyers | Up to 2x | >2x = pause asset group |
| Asset group label | Good/Best | Learning | Low = swap headlines |
| Search terms quality | Legal intent | Mixed | Competitor names = add negatives |

### Optimization triggers
- Day 3: if 0 conversions → verify tracking firing in DevTools before touching campaigns
- Day 4: identify which asset group has Best label → pause Low performers
- Day 5: if lawyers converting but students not → reallocate ₹1,000 from students to lawyers
- Day 7: if 20+ conversions → set Target CPA (students ₹300, lawyers ₹600)

---

## SECTION 8 — IMPLEMENTATION SEQUENCE

- [x] Campaign 1 files archived to Campaign_01_May-Jun2026/
- [x] Campaign 02 folder created
- [x] Google Ads API connected (customers/2183727993)
- [x] Two conversion actions created via API
- [x] Foreign AW- tag identified (AW-17593778001)
- [x] LLM council evaluation completed
- [x] Full live account audit run (2026-06-24) — 3 critical / 3 high / 2 medium / 1 low findings
- [x] Shared negative keyword list built via API (38 keywords, sharedSets/12128615235)
- [ ] Dev fixes 1-4 deployed and verified
- [ ] Anthropic ToS confirmed
- [ ] Higgsfield creatives generated
- [ ] PMax campaigns built via API
- [ ] Campaigns set live
