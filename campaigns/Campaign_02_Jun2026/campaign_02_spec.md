# Anrak Legal — Campaign 02 Spec Sheet
**Budget:** ₹14,000 | **Lawyers:** ₹8,000 | **Students:** ₹6,000
**Objective:** Maximize Conversions (not CPC)
**Date drafted:** 2026-06-24

---

## SECTION 1 — Conversion Tracking (Fix Before Going Live)

### 1A. Two Conversion Events

| Audience | Conversion Event | URL Trigger | Tracking Method |
|---|---|---|---|
| Students | Signup completed | `/onboarding` page load | GTM virtual pageview → Google Ads tag |
| Lawyers | Contact form submitted | `/contact-thank-you` page load | GTM virtual pageview → Google Ads tag |

### 1B. Next.js Virtual Pageview Fix (Dev Task)

**File to create:** `src/components/GTMTracking.tsx`

```tsx
'use client';
import { useEffect, Suspense } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';

function TrackPageView() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  useEffect(() => {
    const url = `${pathname}${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: 'virtual_pageview', page_path: url });
  }, [pathname, searchParams]);
  return null;
}

export default function GTMTracking() {
  return <Suspense fallback={null}><TrackPageView /></Suspense>;
}
```

**Mount in:** `src/app/layout.tsx` — add `<GTMTracking />` as first child of `<body>`

**Dev verification (must confirm before campaign goes live):**
1. Open Chrome DevTools → Console
2. Type `dataLayer` → Enter (note current length)
3. Navigate to `/onboarding` and `/contact-thank-you` in the app
4. Run `dataLayer` again — must see `{event: "virtual_pageview", page_path: "/onboarding"}` and `{event: "virtual_pageview", page_path: "/contact-thank-you"}`

### 1C. GTM Configuration (After dev confirms dataLayer firing)

**Create 2 Data Layer Variables in GTM:**
- Name: `dlv - Page Path` | DL Variable Name: `page_path`

**Create 2 Custom Event Triggers:**
- Trigger 1: Event name `virtual_pageview` | Filter: `dlv - Page Path` equals `/onboarding` | Name: `VPV - Student Signup`
- Trigger 2: Event name `virtual_pageview` | Filter: `dlv - Page Path` equals `/contact-thank-you` | Name: `VPV - Lawyer Contact`

**Create 2 Google Ads Conversion Tags in GTM:**
- Tag 1: fires on `VPV - Student Signup` → maps to Student Signup conversion action in Google Ads
- Tag 2: fires on `VPV - Lawyer Contact` → maps to Lawyer Contact conversion action in Google Ads

**Also add Conversion Linker tag** — fires on all virtual pageviews (both triggers). This preserves the `_gcl_aw` first-party cookie through SPA routing.

---

## SECTION 2 — The 4-Button Rule (User Journey Verification)

Every ad must land the user within 4 clicks of signup or contact form submission.

### Student Journey
```
[Ad Click] → /chat or /feed (1)
→ Click "Sign Up" popup CTA (2)
→ Complete signup form (3)
→ Land on /onboarding (4) ← CONVERSION FIRES
```
Status: ✅ Compliant — 4 steps

### Lawyer Journey
```
[Ad Click] → anrak.legal or feature page (1)
→ Click "Contact Us" or "Book Demo" CTA (2)
→ Fill and submit /contact form (3)
→ Land on /contact-thank-you (4) ← CONVERSION FIRES
```
Status: ✅ Compliant — 4 steps

**Known problem (must fix before launch):** The contact form currently has no Anrak.legal branding or context. It is a dead end. The form page at `/contact` must clearly state what Anrak is and what the lawyer is signing up for. This is a dev/content task, not a Google Ads task.

---

## SECTION 3 — Campaign Architecture (6 Campaigns)

### Bidding Strategy: Maximize Conversions
Do NOT use Manual CPC or Target CPA on day 1. Start with Maximize Conversions with no CPA target. Set a CPA target only after 30+ conversions are recorded. This is Google's recommended approach.

### Budget Allocation

| Campaign | Audience | Daily Budget | Monthly Approx |
|---|---|---|---|
| L1: New Law Firm Setup | Lawyers | ₹400/day | ₹2,800 |
| L2: Legal AI for Practicing Lawyers | Lawyers | ₹350/day | ₹2,450 |
| L3: Claude Wave — Lawyers | Lawyers | ₹400/day | ₹2,800 |  
| S1: Claude Wave — Students | Students | ₹300/day | ₹2,100 |
| S2: AI Tools for Law Students | Students | ₹200/day | ₹1,400 |
| S3: Anrak Brand — Students | Students | ₹350/day | ₹2,450 |
| **Total** | | **₹2,000/day** | **₹14,000** |

Run period: ~7 days. Pause and reallocate budget to best performers after day 4.

---

### CAMPAIGN L1 — "New Law Firm Setup" (₹400/day)

**Goal:** Catch lawyers who are planning to or just starting a law firm. They need operational automation from day 1.

**Landing page:** `anrak.legal` homepage

**Ad Groups:**

**L1-AG1: Starting a Law Firm**
Keywords (Exact + Phrase):
- `[how to start a law firm in india]`
- `[starting a law firm india]`
- `[set up law firm india]`
- `"law firm registration india"`
- `"starting legal practice india"`

Ad copy angle: *"Starting a Law Firm? Run It on AI From Day 1 — Anrak Legal Automates Research, Drafting & Case Files."*

**L1-AG2: Law Firm Operations & Tools**
Keywords:
- `[law firm management software india]`
- `[legal practice management india]`
- `"law firm automation software"`
- `"legal operations software india"`

Ad copy angle: *"Cut Your Firm's Admin Time by 60% — AI That Handles Research, Contracts & Client Docs Automatically."*

**Negative keywords (campaign-level):**
`free`, `student`, `course`, `salary`, `jobs`, `internship`, `llb`, `clat`, `law school`, `moot court`, `harvey`, `vakilsearch`, `casemine`, `casetext`, `maigon`, `legalink`, `legitquest`

---

### CAMPAIGN L2 — "Legal AI for Practicing Lawyers" (₹350/day)

**Goal:** Catch lawyers already in practice who want to automate repetitive tasks — drafting, research, contracts.

**Landing page:** `anrak.legal/chat` or `anrak.legal`

**Ad Groups:**

**L2-AG1: Legal Drafting AI**
Keywords:
- `[ai for legal drafting india]`
- `[legal drafting ai tool]`
- `"ai contract drafting"`
- `"legal document automation india"`
- `[best ai for legal drafting india]`

Ad copy angle: *"Draft Contracts, Petitions & Notices in Minutes — Anrak Legal AI Trained on Indian Case Law."*

**L2-AG2: Legal Research AI**
Keywords:
- `[ai legal research tool india]`
- `[legal research software india]`
- `"ai for case research"`
- `"indian case law ai"`
- `[ai for lawyers india]`

Ad copy angle: *"Research Any Indian Case Law Instantly — AI That Reads Judgments, Statutes & Precedents For You."*

**L2-AG3: Contract Review AI**
Keywords:
- `[ai contract review india]`
- `[contract analysis software india]`
- `"ai agreement review"`
- `"legal document review ai"`

Ad copy angle: *"Review Contracts in 2 Minutes, Not 2 Hours — Anrak AI Flags Risks, Missing Clauses & Red Lines."*

**Negative keywords:** Same as L1 plus `[free]`, `[trial]`, `[open source]`

---

### CAMPAIGN L3 — "Claude Wave — Lawyers" (₹400/day)

**Goal:** Ride the Claude AI wave. Lawyers already using Claude daily → show them Anrak turns Claude into a specialized Indian legal assistant via MCP.

**Landing page:** `anrak.legal/chat` (with visible signup CTA)

**Ad Groups:**

**L3-AG1: Claude for Lawyers**
Keywords:
- `[claude ai for lawyers]`
- `[claude legal assistant]`
- `"claude ai legal india"`
- `"anthropic ai for lawyers"`
- `[claude for legal research]`

Ad copy angle: *"Already Using Claude for Legal Work? Add Anrak MCP — One Click Turns Claude Into India's Best AI Lawyer."*

**L3-AG2: AI Copilot for Lawyers**
Keywords:
- `[ai copilot for lawyers]`
- `[ai legal assistant india]`
- `"personal ai lawyer assistant"`
- `"ai paralegal india"`

Ad copy angle: *"Your Personal AI Paralegal — Anrak Plugs Into Claude, Knows Indian Law, Runs Your Entire Practice."*

**Negative keywords:** Same as L1

---

### CAMPAIGN S1 — "Claude Wave — Students" (₹300/day)

**Goal:** Law students already using Claude → show them Anrak MCP makes Claude 10x better for legal work specifically.

**Landing page:** `anrak.legal/chat`

**Ad Groups:**

**S1-AG1: Claude for Law Students**
Keywords:
- `[claude for law students]`
- `[claude ai legal research]`
- `"claude for moot court"`
- `"best ai for law students"`
- `[ai for llb students]`

Ad copy angle: *"Law Student Using Claude? Add Anrak — 1-Click Install Gives Claude Indian Case Law, Statutes & Moot Court Tools."*

**S1-AG2: Moot Court AI**
Keywords:
- `[moot court ai india]`
- `[ai for moot court preparation]`
- `"moot court memorial ai"`
- `"ai for law competitions"`

Ad copy angle: *"Win Your Moot Court — Anrak AI Researches Cases, Drafts Memorials & Argues Both Sides Instantly."*

**Demographic targeting:** Include 18–24 (unlike lawyer campaigns). Explicit include, not just default.

**Negative keywords:** `free download`, `jobs`, `salary`, `law firm software`, `enterprise`

---

### CAMPAIGN S2 — "AI Tools for Law Students" (₹200/day)

**Goal:** Catch students searching generically for AI tools for legal studies — not necessarily Claude users yet.

**Landing page:** `anrak.legal/feed` or `anrak.legal/chat`

**Ad Groups:**

**S2-AG1: Legal Research for Students**
Keywords:
- `[ai for legal research students]`
- `[legal research tool for students]`
- `"best ai for law students india"`
- `"legal ai for students"`

Ad copy angle: *"Research Any Indian Judgment in 30 Seconds — Free For Law Students. Anrak Legal AI."*

**S2-AG2: Law Assignment & Drafting Help**
Keywords:
- `[ai for law assignments]`
- `[legal drafting help students]`
- `"ai for law essays"`
- `"legal writing ai india"`

Ad copy angle: *"Anrak Helps Law Students Draft Memos, Case Summaries & Legal Arguments — Used by Students at NLSIU, NUJS & More."*

---

### CAMPAIGN S3 — "Anrak Brand — Students" (₹350/day)

**Goal:** Brand building + retargeting. Students who've heard about Anrak or searched for it. Highest intent, lowest cost.

**Landing page:** `anrak.legal` homepage

**Ad Groups:**

**S3-AG1: Anrak Brand**
Keywords:
- `[anrak legal]`
- `[anrak.legal]`
- `"anrak ai"`
- `"anrak legal india"`

Ad copy angle: Direct brand — *"Anrak Legal — India's AI Legal Platform. Research, Draft, Review & Win Cases Faster."*

**S3-AG2: Legal AI India (Generic High Intent)**
Keywords:
- `[legal ai india]`
- `[best legal ai india]`
- `"ai for indian law"`
- `[indian law ai tool]`

---

## SECTION 4 — Ad Schedule (All 6 Campaigns)

| Day | Hours Active |
|---|---|
| Monday–Friday | 9:00 AM – 8:00 PM IST |
| Saturday | 10:00 AM – 2:00 PM IST (students only — S1, S2, S3) |
| Sunday | OFF (all campaigns) |

Lawyers: Monday–Friday only. Students: Monday–Saturday.

**Rationale from Campaign 01 data:** Sunday spend (₹661 on Jun 7) generated zero conversion-intent traffic. Peak hours were 11 AM–4 PM for B2B. Evening 5–8 PM had decent click volume but lower CTR.

---

## SECTION 5 — Google Ads API + Claude Code Automation

### 5A. What We're Building

End-to-end pipeline: Google Ads API → Claude Code → automated daily actions

**Capabilities:**
1. Pull daily performance data (clicks, cost, conversions) via API → generate a Markdown report automatically
2. Detect and block competitor brand queries in real-time
3. Auto-pause ad groups spending without conversions after ₹500 threshold
4. Auto-increase budget on ad groups showing positive ROAS
5. Surface keyword suggestions from search terms report

### 5B. Google Cloud + Ads API Setup (Step-by-Step)

**Step 1 — Google Cloud Project**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create new project → name it `anrak-google-ads`
3. Enable billing on the project

**Step 2 — Enable Google Ads API**
1. In Cloud Console → APIs & Services → Library
2. Search "Google Ads API" → Enable

**Step 3 — OAuth 2.0 Credentials**
1. APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
2. Application type: Desktop App
3. Name: `Anrak Ads Automation`
4. Download the `credentials.json` file — save it to `Campaign_02_Jun2026/secrets/` (do NOT commit to git)

**Step 4 — Developer Token**
1. Go to Google Ads → Tools → API Center
2. Apply for Basic Access developer token
3. This token is account-level — only needed once
4. Save as environment variable `GOOGLE_ADS_DEVELOPER_TOKEN`

**Step 5 — Customer ID**
Your Google Ads account customer ID (format: XXX-XXX-XXXX) → save as `GOOGLE_ADS_CUSTOMER_ID`

**Step 6 — Install Client Library**
```bash
pip install google-ads
```

### 5C. Daily Automation Script (Claude Code runs this)

Save as `Campaign_02_Jun2026/automation/daily_report.py`

```python
# Anrak Legal — Google Ads Daily Report + Auto-Optimizer
# Run daily via Claude Code or cron

import os
from google.ads.googleads.client import GoogleAdsClient
from datetime import date, timedelta

CUSTOMER_ID = os.environ["GOOGLE_ADS_CUSTOMER_ID"]

def get_client():
    return GoogleAdsClient.load_from_env()

def fetch_campaign_performance(client, days=1):
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            campaign.name,
            campaign.status,
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc
        FROM campaign
        WHERE segments.date DURING LAST_{days}_DAYS
        AND campaign.status = 'ENABLED'
        ORDER BY metrics.cost_micros DESC
    """
    response = ga_service.search(customer_id=CUSTOMER_ID, query=query)
    results = []
    for row in response:
        results.append({
            "campaign": row.campaign.name,
            "clicks": row.metrics.clicks,
            "impressions": row.metrics.impressions,
            "cost_inr": row.metrics.cost_micros / 1_000_000,
            "conversions": row.metrics.conversions,
            "ctr": round(row.metrics.ctr * 100, 2),
            "avg_cpc": round(row.metrics.average_cpc / 1_000_000, 2),
        })
    return results

def fetch_search_terms(client):
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            search_term_view.search_term,
            campaign.name,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM search_term_view
        WHERE segments.date DURING LAST_7_DAYS
        ORDER BY metrics.clicks DESC
        LIMIT 50
    """
    response = ga_service.search(customer_id=CUSTOMER_ID, query=query)
    return [{"term": row.search_term_view.search_term,
             "campaign": row.campaign.name,
             "clicks": row.metrics.clicks,
             "cost": row.metrics.cost_micros / 1_000_000,
             "conversions": row.metrics.conversions} for row in response]

def add_negative_keyword(client, campaign_resource_name, keyword_text):
    campaign_criterion_service = client.get_service("CampaignCriterionService")
    operation = client.get_type("CampaignCriterionOperation")
    criterion = operation.create
    criterion.campaign = campaign_resource_name
    criterion.negative = True
    criterion.keyword.text = keyword_text
    criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.EXACT
    campaign_criterion_service.mutate_campaign_criteria(
        customer_id=CUSTOMER_ID, operations=[operation]
    )
    print(f"Added negative keyword: [{keyword_text}]")

BLOCKLIST = [
    "harvey", "vakilsearch", "casemine", "casetext", "maigon",
    "legalink", "legitquest", "spellbook", "draftbot", "zoho",
    "free", "jobs", "salary", "course", "clat", "syllabus", "internship"
]

def auto_block_bad_terms(client, search_terms):
    ga_service = client.get_service("GoogleAdsService")
    campaign_query = "SELECT campaign.resource_name, campaign.name FROM campaign WHERE campaign.status = 'ENABLED'"
    campaigns = {row.campaign.name: row.campaign.resource_name
                 for row in ga_service.search(customer_id=CUSTOMER_ID, query=campaign_query)}
    
    blocked = []
    for entry in search_terms:
        term = entry["term"].lower()
        if any(bad in term for bad in BLOCKLIST):
            campaign_rn = campaigns.get(entry["campaign"])
            if campaign_rn:
                add_negative_keyword(client, campaign_rn, entry["term"])
                blocked.append(entry["term"])
    return blocked

def generate_markdown_report(performance, search_terms, blocked):
    today = date.today().isoformat()
    lines = [f"# Anrak Ads Daily Report — {today}\n"]
    lines.append("## Campaign Performance (Last 24h)\n")
    lines.append("| Campaign | Clicks | Impr | CTR | Cost (₹) | Conv | Avg CPC |")
    lines.append("|---|---|---|---|---|---|---|")
    for p in performance:
        lines.append(f"| {p['campaign']} | {p['clicks']} | {p['impressions']} | {p['ctr']}% | ₹{p['cost_inr']:.2f} | {p['conversions']} | ₹{p['avg_cpc']} |")
    
    lines.append("\n## Top Search Terms (Last 7 Days)\n")
    lines.append("| Term | Clicks | Cost | Conv |")
    lines.append("|---|---|---|---|")
    for s in search_terms[:20]:
        lines.append(f"| {s['term']} | {s['clicks']} | ₹{s['cost']:.2f} | {s['conversions']} |")
    
    if blocked:
        lines.append(f"\n## Auto-Blocked Terms ({len(blocked)})\n")
        for b in blocked:
            lines.append(f"- `{b}`")
    
    report_path = f"Campaign_02_Jun2026/reports/report_{today}.md"
    os.makedirs("Campaign_02_Jun2026/reports", exist_ok=True)
    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Report saved: {report_path}")
    return report_path

if __name__ == "__main__":
    client = get_client()
    perf = fetch_campaign_performance(client)
    terms = fetch_search_terms(client)
    blocked = auto_block_bad_terms(client, terms)
    generate_markdown_report(perf, terms, blocked)
```

### 5D. Environment Variables Required

Create file `Campaign_02_Jun2026/secrets/.env` (never commit this):
```
GOOGLE_ADS_DEVELOPER_TOKEN=your_token_here
GOOGLE_ADS_CLIENT_ID=your_oauth_client_id
GOOGLE_ADS_CLIENT_SECRET=your_oauth_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_manager_account_id (if using MCC)
```

### 5E. How Claude Code Uses This

Once the API is set up, you can run in Claude Code:
- `python daily_report.py` → generates today's markdown report automatically
- Ask Claude to analyze the report and suggest bid changes
- Ask Claude to write new ad copy based on top search terms
- Claude can modify the script to add new automation rules

---

## SECTION 6 — Key Decisions to Verify (Explicit Sign-Off Required)

Before any campaign goes live, confirm each item:

| # | Decision | Status |
|---|---|---|
| 1 | Budget split: ₹8,000 lawyers / ₹6,000 students | ☐ Confirmed |
| 2 | Bidding: Maximize Conversions (no CPA target until 30+ conversions) | ☐ Confirmed |
| 3 | Student conversion fires on `/onboarding` page load | ☐ Confirmed |
| 4 | Lawyer conversion fires on `/contact-thank-you` page load | ☐ Confirmed |
| 5 | Contact form `/contact` page has Anrak context added (dev task) | ☐ Dev confirms done |
| 6 | GTM virtual pageview fix deployed and verified via dataLayer | ☐ Dev confirms done |
| 7 | GTM conversion tags created and tested in Preview mode | ☐ Confirmed |
| 8 | Ad schedule: Lawyers Mon–Fri 9AM–8PM, Students Mon–Sat 9AM–8PM | ☐ Confirmed |
| 9 | 18–24 age group INCLUDED in student campaigns, EXCLUDED in lawyer campaigns | ☐ Confirmed |
| 10 | Google Cloud project `anrak-google-ads` created and Ads API enabled | ☐ Dev confirms done |

---

## SECTION 7 — What Does NOT Go Live Until Fixed

1. **GTM virtual pageview fix** — without this, 0 conversions will be tracked again and Maximize Conversions bidding will have no signal to optimize on. This is a hard blocker.
2. **Contact form `/contact` page** — currently no Anrak context. Lawyers land on a dead-end form. Add at minimum: what they're contacting about, what Anrak does, and what happens after they submit.
3. **Google Ads API setup** — this is not a blocker for campaign launch, but must be done in parallel so automation is live from day 1.
