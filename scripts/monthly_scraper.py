"""
monthly_scraper.py
Usage: python monthly_scraper.py
Scrapes 4 public data sources. No login. No browser automation.
Output: review/YYYY-MM_market_intel.md
After running, open Claude Code and run /ads-council for analysis.
"""
import sys
import os
import json
import re
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

try:
    import requests
    import feedparser
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip install -r requirements.txt")
    sys.exit(1)

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW = os.path.join(ROOT, "review")

SOURCES = {
    "google_ads_blog": {
        "name": "Google Ads Developer Blog",
        "url": "https://ads-developers.googleblog.com/feeds/posts/default?max-results=10",
        "type": "rss",
    },
    "search_engine_land_pmax": {
        "name": "Search Engine Land — PMax",
        "url": "https://searchengineland.com/feed?s=performance+max",
        "type": "rss",
    },
    "reddit_ppc": {
        "name": "Reddit r/PPC",
        "url": "https://www.reddit.com/r/PPC/.json?limit=20&sort=hot",
        "type": "reddit",
    },
    "wordstream_benchmarks": {
        "name": "WordStream Google Ads Benchmarks",
        "url": "https://www.wordstream.com/blog/ws/2016/02/29/google-adwords-industry-benchmarks",
        "type": "scrape",
    },
}

KEYWORDS = [
    "performance max", "pmax", "india", "legal", "saas", "cpa", "ctr",
    "smart bidding", "audience signals", "search themes", "asset group",
    "conversion", "google ads api", "v24", "v25",
]

def fetch_rss(url, source_name):
    items = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            title   = getattr(entry, "title", "")
            summary = getattr(entry, "summary", "")
            link    = getattr(entry, "link", "")
            text    = (title + " " + summary).lower()
            relevant = any(kw in text for kw in KEYWORDS)
            items.append({
                "title": title,
                "link": link,
                "summary": summary[:200],
                "relevant": relevant,
            })
    except Exception as e:
        items.append({"title": f"ERROR: {e}", "link": "", "summary": "", "relevant": False})
    return items

def fetch_reddit(url, source_name):
    items = []
    try:
        headers = {"User-Agent": "google-ads-automation/1.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        posts = data.get("data", {}).get("children", [])
        for post in posts[:15]:
            p = post.get("data", {})
            title = p.get("title", "")
            text  = title.lower()
            relevant = any(kw in text for kw in KEYWORDS)
            items.append({
                "title": title,
                "link": f"https://reddit.com{p.get('permalink', '')}",
                "summary": p.get("selftext", "")[:200],
                "relevant": relevant,
            })
    except Exception as e:
        items.append({"title": f"ERROR: {e}", "link": "", "summary": "", "relevant": False})
    return items

def fetch_scrape(url, source_name):
    items = []
    try:
        headers = {"User-Agent": "google-ads-automation/1.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Extract tables or stat-like paragraphs
        tables = soup.find_all("table")
        for table in tables[:2]:
            rows = table.find_all("tr")
            for row in rows[:20]:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if cells:
                    text = " | ".join(cells)
                    relevant = any(kw in text.lower() for kw in KEYWORDS + ["legal", "ctr", "cpa", "cpc", "%"])
                    if relevant:
                        items.append({
                            "title": text[:120],
                            "link": url,
                            "summary": "",
                            "relevant": True,
                        })
        if not items:
            items.append({"title": "No structured table data found on page", "link": url, "summary": "", "relevant": False})
    except Exception as e:
        items.append({"title": f"ERROR: {e}", "link": "", "summary": "", "relevant": False})
    return items

def build_report(month, all_data):
    lines = []
    lines.append(f"# Market Intelligence — {month}")
    lines.append(f"**Generated:** {date.today()} | Sources: {len(all_data)}\n")
    lines.append("---\n")

    for source_key, items in all_data.items():
        source = SOURCES[source_key]
        lines.append(f"## {source['name']}\n")

        relevant = [i for i in items if i["relevant"]]
        other    = [i for i in items if not i["relevant"]]

        if relevant:
            lines.append(f"**Flagged as relevant to Anrak campaigns ({len(relevant)} items):**\n")
            for item in relevant:
                lines.append(f"- [{item['title']}]({item['link']})")
                if item["summary"]:
                    lines.append(f"  > {item['summary'][:150]}")
        else:
            lines.append("_No items matched relevance keywords this month._")

        if other:
            lines.append(f"\n<details><summary>Other items ({len(other)})</summary>\n")
            for item in other[:5]:
                lines.append(f"- [{item['title']}]({item['link']})")
            lines.append("</details>")

        lines.append("")

    lines.append("---")
    lines.append("## Council Analysis")
    lines.append("_This section is filled by the 4-layer LLM council._\n")
    lines.append("**Status:** PENDING COUNCIL ANALYSIS\n")
    lines.append("Open Claude Code and run:")
    lines.append("```")
    lines.append("/ads-council")
    lines.append("```")
    lines.append("The council will read this report and surface actionable signals for your next campaign.")

    return "\n".join(lines)

def main():
    month = date.today().strftime("%Y-%m")
    print(f"Scraping market intelligence for {month}...")
    print("Sources: Google Ads Blog, Search Engine Land, Reddit r/PPC, WordStream\n")

    all_data = {}

    for key, source in SOURCES.items():
        print(f"  Fetching: {source['name']}...")
        if source["type"] == "rss":
            all_data[key] = fetch_rss(source["url"], source["name"])
        elif source["type"] == "reddit":
            all_data[key] = fetch_reddit(source["url"], source["name"])
        elif source["type"] == "scrape":
            all_data[key] = fetch_scrape(source["url"], source["name"])
        relevant_count = sum(1 for i in all_data[key] if i["relevant"])
        print(f"    Done. {relevant_count} relevant items found.")

    report = build_report(month, all_data)

    os.makedirs(REVIEW, exist_ok=True)
    out = os.path.join(REVIEW, f"{month}_market_intel.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nSaved to: {out}")
    print("\nNext: open Claude Code and run /ads-council to analyze this report.")

if __name__ == "__main__":
    main()
