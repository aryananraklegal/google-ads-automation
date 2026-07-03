# Campaign 02 — 14-Day Flight Plan
**Account:** customers/2183727993
**Campaigns:** PMax-Students (23976339058) / PMax-Lawyers (23966712858)
**Budget:** ₹700/day students · ₹300/day lawyers · ₹14,000 total
**Status:** PAUSED — enabling blocked by Phase 0 items below
**Last updated:** 2026-06-25

---

## PHASE 0 — Pre-Launch (before enabling either campaign)

All items must reach ✅ before any campaign is set ENABLED.

### 0-A: Dev Tasks
| ID | Task | Owner | Done? |
|---|---|---|---|
| H6 | `onboarding-form.tsx` — add `event_timeout: 2000` + already-redirected boolean guard + fallback `router.push` if gtag absent | Dev | ☐ |
| H7 | `ConversionFire.tsx` — gate fire behind `sessionStorage` submit-token. Token set at form submit, consumed once on page load, cleared after fire | Dev | ☐ |

**Verification (dev runs in Chrome DevTools after deploying):**
- Student: complete test signup → Network tab → confirm hit to `googleads.googleapis.com` label `cqpwCLDpzsQcEKCi4v1C`
- Lawyer: submit contact form → load `/contact-thank-you` → confirm label `pCMiCLPpzsQcEKCi4v1C` fires once → direct URL reload must NOT fire again

### 0-B: Google Ads UI Tasks (Kapil)
| ID | Task | Where | Done? |
|---|---|---|---|
| U1 | Demote ALL conversion actions EXCEPT 7660090544 and 7660090547 to "Include in Conversions = No (Secondary)" | Tools → Conversions → each action → Settings | ☐ |
| U2 | Final URL expansion OFF — Student campaign | Campaign settings → URL options | ☐ |
| U3 | Final URL expansion OFF — Lawyer campaign | Campaign settings → URL options | ☐ |

### 0-C: Copy Rewrites ✅ COMPLETE — NO ACTION NEEDED
Verified 2026-06-25 via API query. None of the 3 flagged headlines ("Beat Every Opposing Counsel", "Law School's Best AI Tool", "Indian Advocates Cut Drafting Time by 60%") are in the live campaigns. Build scripts used cleaner copy. All 15 student + 15 lawyer headlines confirmed clean.

**Decision logged:** "Claude" in ad copy — accepted risk, no rewrite.

### 0-D: Bidding Confirmation
Both campaigns: **Maximize Conversions, no tCPA, for the full 14 days.**
No mid-flight bidding changes. This is locked.

---

## PHASE 1 — Enable

Once all Phase 0 items are ✅:

1. Claude Code sets both campaigns status = ENABLED via API
2. Confirm in UI both campaigns show "Eligible" or "Active"
3. Note exact enable timestamp — Day 1 starts from this moment

---

## PHASE 2 — Daily Monitoring (Day 1–14)

**Owner:** Claude Code runs monitoring script on-demand each morning. Kapil reviews output.

### Thresholds

| Metric | Green | Yellow | Red |
|---|---|---|---|
| Impressions/day | >500 | 100–500 | <100 |
| Student CTR | >4% | 2–4% | <2% |
| Lawyer CTR | >2% | 1–2% | <1% |
| Conversions day 1–3 | Any | 0 after day 2 | 0 on day 3 → stop, verify tracking |
| Student CPA | <₹150 | ₹150–300 | >₹300 → pause + diagnose |
| Lawyer CPA | <₹600 | ₹600–900 | >₹900 → pause lawyer campaign |
| Budget utilization | 90–100% | 70–90% | <70% → check campaign status |
| Ad disapprovals | 0 | 1–2 minor | Any trademark → pause + rewrite |
| Asset label (day 5+) | Good/Best | Learning | Low → swap headlines |

### Check Schedule

| Day | What Claude pulls | Action if Red |
|---|---|---|
| 1 | Impressions, conversion count | 0 impressions = check campaign status in UI |
| 3 | Conversions, CPA | 0 conversions = DevTools test before touching anything |
| 5 | Asset group labels, CTR | Pause any "Low" asset group |
| 7 | Search terms report, CPA, budget pace | Add irrelevant queries to negative list |
| 10 | Device split, placement report | Mobile CPA >2x desktop → flag LP mobile experience |
| 14 | Full audit | Document actuals vs projections |

### Day 3 Rule
If 0 conversions on day 3: **do not touch bids or budgets.** First verify tracking fires in DevTools on a real test conversion. Only diagnose campaigns after tracking is confirmed.

---

## PHASE 3 — Day 14 Wrap-Up

Claude Code pulls final report:
- Total conversions: students / lawyers
- Actual CPA: students / lawyers
- Budget spent vs allocated
- Top-performing headlines (asset labels)
- Search terms that drove conversions
- Any disapprovals or policy issues

Output used to brief Campaign 03.

---

## POST-LAUNCH (within 72h, non-blocking)

| ID | Task | Owner |
|---|---|---|
| H9 | Enhanced conversions: pass `sha256_email_address` in gtag student conversion call | Dev |
| M3 | DPDP Consent Mode v2 — default denied state for Indian visitors | Dev |
| M2 | Verify `sharedSets/12128615235` appears under both PMax campaign negative keyword tabs in UI | Kapil |
| AUD | Query account for `customers/2183727993/audiences/{id}` matching "All Visitors" → attach to both AGs via AssetGroupSignalService | Claude Code |

---

## REFERENCE

| Item | Value |
|---|---|
| Student campaign RN | customers/2183727993/campaigns/23976339058 |
| Lawyer campaign RN | customers/2183727993/campaigns/23966712858 |
| Student asset group RN | customers/2183727993/assetGroups/6724850654 |
| Lawyer asset group RN | customers/2183727993/assetGroups/6724984923 |
| Student conversion | ID 7660090544 · label cqpwCLDpzsQcEKCi4v1C |
| Lawyer conversion | ID 7660090547 · label pCMiCLPpzsQcEKCi4v1C |
| Shared negative list | customers/2183727993/sharedSets/12128615235 |
| Credentials | Campaign_02_Jun2026/secrets/google-ads.yaml |
