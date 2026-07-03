# Anrak Legal: B2B Google Ads Playbook
**Framework for Tiny-Budget B2B Legal Tech Acquisition (India First)**

This playbook is the foundational strategy document for Anrak Legal's Google Ads positioning and campaign execution. It is designed to maximize the impact of a highly constrained daily budget (₹400/day) targeting Enterprise+ (Big Law Indian Law Firms), leveraging the Anthropic Claude Pro partnership, and avoiding common budget-wasting pitfalls.

---

## 1. Executive Summary & Core Positioning

| Element | Strategy | Strategy Rationale |
| :--- | :--- | :--- |
| **Target Audience** | Tier-1 & Tier-2 Indian Law Firms (Enterprise+ ICP) | Big Law decision-makers have high contract value, justifying high-intent acquisition costs. |
| **Primary Value Hook** | Tiered Partnership with Anthropic (Free Claude Pro with Enterprise+ Subscription) | Co-branding with Anthropic is the strongest weapon against Harvey (OpenAI-backed) and Legora. |
| **Geographic Scope** | India Only (Strict Presence) | Indian CPCs (₹50 - ₹250) are cheaper than the US/UK, allowing validation before global expansion. |
| **Budget Constraint** | ₹400/Day (~$5 USD/Day) | Extremely tight. Requires surgical targeting, defensive bidding, and high pre-qualification. |
| **Temporary Routing** | Gated `/contact` page with pre-qualifying copy | Stopgap solution for 1 week until the dedicated Enterprise+ / Anthropic landing page is live. |

> [!WARNING]
> **Tri Legal Reference Ban:** Tri Legal is strictly for internal discussions. Do **NOT** use "Tri Legal" in any search ad copy, keywords, assets, or public landing pages.

---

## 2. Website Audit Context & Conversion Alignment
Based on the [anraklegal_website_forensic_audit.md](file:///c:/Users/HP/OneDrive/Documents/Anrak/anrak_legal_pitch_deck/AnrakLegal_x_Khaitan/01_Research_and_Context/anraklegal_website_forensic_audit.md), we must align campaign endpoints to prevent traffic leakage:

1.  **Resolve Pricing Inconsistencies:** The audit revealed that `/chatgpt` displays `Starter / Advanced` while `/pricing` displays `Professional / Enterprise / Enterprise+`. Ensure the engineering team unifies these on the live site to avoid losing user trust.
2.  **Conversion Funnel Hardening:** Conversion tracking must be verified on the `/contact` sales page. Google Ads must only optimize for actual lead captures (e.g., submitted forms, demo bookings), not generic page views or initial token usage.
3.  **Strict Landing Page Segmentation:** For B2B enterprise targets, avoid sending traffic to the homepage (`/`), as its broad structure increases comprehension burden. Route them directly to `/contact` for high-intent queries, and `/docs` for developer-facing queries.

---

## 3. The DO's: Actionable Blueprint for Tiny Budgets

### Campaign Structure & Bidding
*   **DO Stick to ONE Campaign Type (Search Only):** Keep 100% of the budget focused on Google Search Ads. Turn off **Display Network** and **Search Partners**. Avoid **Performance Max (PMax)**, as PMax spreads tiny budgets too thin across YouTube/Gmail and requires a large history of conversions to optimize successfully.
*   **DO Focus on ONE Core Offer:** Target the Enterprise+ tier exclusively. The high contract value of big law deals justifies the acquisition cost, whereas advertising cheap document templates (`/contracts`) will yield high clicks but low-revenue PLG conversions that won't impress investors.
*   **DO Bidding Strategy - Clicks with Max CPC Cap:** For a new account with no conversion history, start with **Maximize Clicks** but set a strict **Maximum CPC limit** (e.g., ₹100–₹120). This ensures a single click doesn't consume 50%+ of your daily ₹400 budget. Transition to **Maximize Conversions** only after gathering 15-30 steady conversions.
*   **DO Set Target Locations to "Presence Only":** In the location options, select *"Presence: People in or regularly in your targeted locations."* This prevents Google from showing ads to searchers in other countries who are simply "interested in" India.

### Keyword Management
*   **DO Use Exact Match `[...]` and Phrase Match `"..."` Strictly:** Target long-tail, high-intent keywords that signal an enterprise searcher (e.g., `[ai legal assistant for law firms]`, `[legal document automation software enterprise]`, `"ai software for corporate law firms"`).
*   **DO Build a Robust Pre-emptive Negative Keyword List:** Block words that imply a non-enterprise searcher.
    *   *Examples:* `free`, `template`, `DIY`, `student`, `internship`, `jobs`, `career`, `how to`, `pro bono`, `course`, `download`.

### Ad Copy & Pre-qualification
*   **DO Pre-qualify Users in the Ad Copy:** Use your headlines to repel solo lawyers, small businesses, and students before they click.
    *   *Ad Copy Filter Hook:* `"Designed for Law Firms"` or `"Enterprise Law Firms Only"`
    *   *Pricing Filter Hook:* `"Plans from ₹X,XXX/mo"` (prevents small-budget searchers from clicking).
*   **DO Pin Pre-qualifying Headlines:** Pin your pre-qualification headline to **Position 1** to ensure every searcher sees it instantly.
*   **DO Highlight the Anthropic Collaboration:** Leverage the co-branding.
    *   *Headline Example:* `"Anrak Legal OS - Inc. Claude Pro"` or `"Get Claude Pro Free on Anrak"`

### Optimization Rules
*   **DO Optimize Early and Aggressively:** In a tiny budget campaign, you cannot wait for statistical significance. If a keyword spends ₹200 (half your daily budget) with 0 conversions and a high cost-per-click, **pause it immediately**. Be trigger-happy and reallocate the budget to your top-performing search queries.

---

## 4. The DONT's: Critical Pitfalls to Avoid

*   **DON'T Use Broad Match Keywords:** Standard broad match (e.g., `legal ai`) is too loose. It will trigger your ads on queries like "is legal ai safe" or "artificial intelligence tools," completely blowing your ₹400 daily budget in minutes on useless clicks.
*   **DON'T Target High-Cost, Generic B2B Keywords:** Avoid broad terms like `legal software` or `law firm tech`. Bidding on these puts you in direct competition with global legacy software vendors, driving your CPC out of reach. Focus on specific, niche search intents.
*   **DON'T Split the Budget:** Do not run multiple campaigns simultaneously. If you have a ₹400 daily limit, splitting it into two campaigns of ₹200 each leaves neither campaign with enough daily click volume to feed Google's optimization algorithms.
*   **DON'T Advertise Internationally (Yet):** Keep the US, UK, HK, and China campaigns paused until the India market demonstrates a positive CAC-to-LTV ratio and the landing pages are fully optimized.
*   **DON'T Neglect the Search Terms Report:** Never let the campaign run for more than 48 hours without reviewing the actual search queries. Add any irrelevant query to the negative keyword list immediately.

---

## 5. Campaign Audit Checklist (For Kapil's Pre-existing Ad)

Use this step-by-step checklist to review the current active Google Ad campaign:

1.  [ ] **Campaign Type:** Is it a *Search* campaign? (If it's Display, Video, or Performance Max, mark it for immediate pausing).
2.  [ ] **Networks:** Are *Display Network* and *Search Partners* unchecked?
3.  [ ] **Locations:** Is the target strictly set to *India*? Is the location option set to *Presence* instead of *Presence or Interest*?
4.  [ ] **Keywords:** Are there any Broad Match keywords? (If yes, change them to Phrase or Exact Match).
5.  [ ] **Negative Keywords:** Has a list of negative keywords (free, jobs, template, etc.) been applied?
6.  [ ] **Pre-qualification:** Does the ad copy clearly communicate that it is an enterprise product for law firms to deter unqualified clicks?
7.  [ ] **Tracking:** Go to the "Conversions" menu. Are the tracking status tags green and active? Are they measuring key actions on the landing page?
8.  [ ] **Landing Page Destination:** Where does the ad send clicks? (If it's the homepage `/` or `/contracts` template page, prepare to redirect it to `/contact` for Enterprise+).
