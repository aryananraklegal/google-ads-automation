"""
campaign_interview.py
Usage: python campaign_interview.py
Saves progress automatically. Resume anytime by re-running.
Output: CAMPAIGN_BRIEF.md in the current folder.
"""
import sys
import os
import json
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT_FILE = os.path.join(ROOT, ".interview_draft.json")
OUTPUT     = os.path.join(ROOT, "CAMPAIGN_BRIEF.md")

FIELDS = [
    {
        "key": "campaign_name",
        "prompt": "Campaign name (e.g. PMax-Students-Aug2026):",
        "hint": None,
        "required": True,
    },
    {
        "key": "start_date",
        "prompt": "Start date (YYYY-MM-DD):",
        "hint": f"Today is {date.today()}",
        "required": True,
    },
    {
        "key": "end_date",
        "prompt": "End date (YYYY-MM-DD):",
        "hint": "Recommended: 14-day minimum for PMax learning phase",
        "required": True,
    },
    {
        "key": "total_budget",
        "prompt": "Total budget (₹):",
        "hint": "e.g. 14000 for a 14-day ₹1000/day campaign",
        "required": True,
    },
    {
        "key": "budget_split",
        "prompt": "Daily budget split across campaigns (e.g. '70% Students / 30% Lawyers' or 'All Students'):",
        "hint": None,
        "required": True,
    },
    {
        "key": "primary_goal",
        "prompt": "Primary goal — what counts as a conversion?",
        "hint": "Options: student_signup / lawyer_demo / lawyer_contact / other (describe)",
        "required": True,
    },
    {
        "key": "target_cpa",
        "prompt": "Target CPA per conversion (₹):",
        "hint": "Benchmarks: Students ₹150–300 | Lawyers ₹600–1200 (India, legal SaaS, 2026)",
        "required": True,
    },
    {
        "key": "geo",
        "prompt": "Geographic targeting:",
        "hint": "e.g. 'All India' / 'Mumbai, Delhi, Bangalore' / 'Tier 1 cities'",
        "required": True,
    },
    {
        "key": "audience_description",
        "prompt": "Describe the target customer in 2 sentences:",
        "hint": "Be specific: role, pain point, where they are in the funnel",
        "required": True,
    },
    {
        "key": "landing_page",
        "prompt": "Landing page URL:",
        "hint": "e.g. https://anrak.legal/feed",
        "required": True,
    },
    {
        "key": "conversion_action",
        "prompt": "What does the user do on the landing page to convert?",
        "hint": "e.g. 'Clicks sign up > fills form > reaches /onboarding'",
        "required": True,
    },
    {
        "key": "conversion_tag",
        "prompt": "Google Ads conversion label (send_to value):",
        "hint": "e.g. AW-17980494112/cqpwCLDpzsQcEKCi4v1C — leave blank if not yet set up",
        "required": False,
    },
    {
        "key": "audience_signals",
        "prompt": "Audience signals to add to PMax (comma-separated, or 'none'):",
        "hint": "e.g. 'Law students India, Legal software intenders, Competitor visitors (Manupatra)'",
        "required": False,
    },
    {
        "key": "search_themes",
        "prompt": "Search themes / keyword topics to guide PMax (comma-separated, or 'none'):",
        "hint": "e.g. 'legal AI India, moot court research, advocate case management software'",
        "required": False,
    },
    {
        "key": "creative_available",
        "prompt": "What creative assets are ready? (describe what you have)",
        "hint": "e.g. '3 images, 1 YouTube video, 5 headlines' or 'nothing yet'",
        "required": True,
    },
    {
        "key": "previous_campaign_learnings",
        "prompt": "Key learnings from the previous campaign to apply here:",
        "hint": "e.g. '99% mobile, content-first funnel needs stronger CTA, no audience signals last time'",
        "required": False,
    },
    {
        "key": "hard_constraints",
        "prompt": "Any hard constraints or things we must NOT do:",
        "hint": "e.g. 'No direct /signup landing page', 'Budget cannot exceed ₹1000/day'",
        "required": False,
    },
]

def load_draft():
    if os.path.exists(DRAFT_FILE):
        with open(DRAFT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_draft(answers):
    with open(DRAFT_FILE, "w", encoding="utf-8") as f:
        json.dump(answers, f, indent=2, ensure_ascii=False)

def ask_field(field, existing):
    key   = field["key"]
    if key in existing and existing[key]:
        print(f"\n  [{key}] Already answered: {existing[key]}")
        change = input("  Change this? [y/N] > ").strip().lower()
        if change != "y":
            return existing[key]

    print(f"\n{'─'*50}")
    print(f"  {field['prompt']}")
    if field["hint"]:
        print(f"  Hint: {field['hint']}")
    if not field["required"]:
        print("  (Optional — press Enter to skip)")

    while True:
        val = input("  > ").strip()
        if val:
            return val
        if not field["required"]:
            return ""
        print("  This field is required.")

def run_interview():
    print("\n" + "="*60)
    print("  Campaign Interview")
    print("  Answer each question. Progress saves automatically.")
    print("  Re-run at any time to resume or change an answer.")
    print("="*60)

    answers = load_draft()
    if answers:
        filled = sum(1 for v in answers.values() if v)
        print(f"\n  Resuming. {filled}/{len(FIELDS)} fields already filled.")

    for field in FIELDS:
        answers[field["key"]] = ask_field(field, answers)
        save_draft(answers)

    return answers

def generate_brief(answers):
    a = answers
    lines = []
    lines.append(f"# Campaign Brief — {a.get('campaign_name', 'Untitled')}")
    lines.append(f"**Generated:** {date.today()}\n")

    lines.append("## Flight")
    lines.append(f"- **Dates:** {a.get('start_date')} → {a.get('end_date')}")
    lines.append(f"- **Total budget:** ₹{a.get('total_budget')}")
    lines.append(f"- **Budget split:** {a.get('budget_split')}")
    lines.append(f"- **Geography:** {a.get('geo')}\n")

    lines.append("## Goal")
    lines.append(f"- **Conversion event:** {a.get('primary_goal')}")
    lines.append(f"- **Target CPA:** ₹{a.get('target_cpa')}")
    lines.append(f"- **Conversion action on page:** {a.get('conversion_action')}")
    lines.append(f"- **Conversion tag:** {a.get('conversion_tag') or 'Not yet set up'}\n")

    lines.append("## Audience")
    lines.append(f"- **Who:** {a.get('audience_description')}")
    lines.append(f"- **Audience signals:** {a.get('audience_signals') or 'None'}")
    lines.append(f"- **Search themes:** {a.get('search_themes') or 'None'}\n")

    lines.append("## Landing")
    lines.append(f"- **URL:** {a.get('landing_page')}\n")

    lines.append("## Creative")
    lines.append(f"- **Available:** {a.get('creative_available')}\n")

    lines.append("## Context")
    lines.append(f"- **Previous learnings:** {a.get('previous_campaign_learnings') or 'None'}")
    lines.append(f"- **Hard constraints:** {a.get('hard_constraints') or 'None'}\n")

    lines.append("---")
    lines.append("## LLM Council Review")
    lines.append("_This section is filled by the 4-layer council. Do not edit manually._\n")
    lines.append("**Status:** PENDING COUNCIL REVIEW\n")
    lines.append("Once this brief is complete, open Claude Code and run:")
    lines.append("```")
    lines.append("/ads-council")
    lines.append("```")
    lines.append("The council will review this brief, flag inconsistencies, and produce a GO / NO-GO verdict before any campaign is created.")

    return "\n".join(lines)

def main():
    answers = run_interview()

    print("\n" + "="*60)
    print("  All fields complete. Generating CAMPAIGN_BRIEF.md...")

    brief = generate_brief(answers)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(brief)

    # Clean up draft
    if os.path.exists(DRAFT_FILE):
        os.remove(DRAFT_FILE)

    print(f"  Saved to: {OUTPUT}")
    print("""
  Next step:
  Open Claude Code in this folder and run:
    /ads-council
  The 4-layer council will review your brief before any campaign is built.
""")

if __name__ == "__main__":
    main()
