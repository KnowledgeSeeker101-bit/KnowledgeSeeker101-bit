import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote_plus
import feedparser

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_CATEGORIES = ["cs.AI", "cs.LG"]
MAX_ARTICLES = 5

def fetch_arxiv():
    query = " OR ".join(f"cat:{c}" for c in ARXIV_CATEGORIES)
    params = {
        "search_query": query,
        "max_results": 1,
        "start": 0,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    url = ARXIV_API + "?" + "&".join(f"{k}={quote_plus(str(v))}" for k,v in params.items())
    resp = requests.get(url, headers={"User-Agent": "GitHub-Actions"}, timeout=10)
    resp.raise_for_status()
    return resp.text

def parse_arxiv(xml_text):
    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", ns)
    if entry is None:
        return None
    title = entry.find("atom:title", ns).text.strip()
    summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
    link = entry.find("atom:id", ns).text.strip()
    aid = link.split("/")[-1]
    return {
        "title": title,
        "summary": summary[:800] + "...",
        "abs": link,
        "pdf": f"https://arxiv.org/pdf/{aid}.pdf"
    }

# ---- Dev.to ----
def fetch_devto_articles():
    articles = []
    try:
        url = "https://dev.to/api/articles?per_page=10&top=7"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            for article in r.json()[:MAX_ARTICLES]:
                articles.append({
                    'title': article.get('title', 'Untitled'),
                    'description': article.get('description', '')[:200],
                    'url': article.get('url', '#'),
                    'published': article.get('published_at', '')[:10],
                    'tags': article.get('tag_list', [])[:3],
                    'reactions': article.get('public_reactions_count', 0),
                    'reading_time': article.get('reading_time_minutes', 5),
                    'source': 'Dev.to'
                })
    except Exception:
        pass
    return articles

# ---- Hacker News ----
def fetch_hackernews():
    articles = []
    try:
        r = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        ids = r.json()[:10]
        for sid in ids[:MAX_ARTICLES]:
            try:
                s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
                if s.get("type") == "story" and s.get("url"):
                    articles.append({
                        'title': s.get('title', ''),
                        'description': s.get('title', '')[:200],
                        'url': s.get('url'),
                        'published': datetime.fromtimestamp(s.get('time', 0)).strftime("%Y-%m-%d"),
                        'tags': ['tech'],
                        'reactions': s.get('score', 0),
                        'reading_time': 5,
                        'source': 'Hacker News'
                    })
            except Exception:
                continue
    except Exception:
        pass
    return articles

# ---- Medium ----
def fetch_medium_rss():
    articles = []
    try:
        feed = feedparser.parse("https://medium.com/feed/tag/technology")
        for entry in feed.entries[:MAX_ARTICLES]:
            summary = entry.get('summary', '')
            summary = summary.replace("<p>", "").replace("</p>", "")
            articles.append({
                'title': entry.get('title', ''),
                'description': summary[:200],
                'url': entry.get('link'),
                'published': entry.get('published', '')[:10],
                'tags': ['tech'],
                'reactions': 0,
                'reading_time': 5,
                'source': 'Medium'
            })
    except Exception:
        pass
    return articles

def get_tech_articles():
    sources = [fetch_devto_articles, fetch_hackernews, fetch_medium_rss]
    collected = []
    for fetch in sources:
        try:
            items = fetch()
            collected.extend(items)
        except Exception:
            pass
        if len(collected) >= MAX_ARTICLES:
            break

    # dedupe
    unique = []
    seen = set()
    for a in collected:
        if a["title"] not in seen:
            seen.add(a["title"])
            unique.append(a)
        if len(unique) >= MAX_ARTICLES:
            break

    return unique

def main():
    xml = fetch_arxiv()
    paper = parse_arxiv(xml)
    tech = get_tech_articles()

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    banner = "https://svg-banners.vercel.app/api?type=luminance&text1=AI+Research+Digest&width=900&height=200"

    md = f"""<p align="center"><img src="{banner}" /></p>

# Latest AI Research (arXiv)

_Last updated: {now}_

"""

    if paper:
        md += f"""### **[{paper['title']}]({paper['abs']})**

**Abstract:**  
{paper['summary']}

📄 [Read Paper]({paper['abs']})  
📘 [PDF]({paper['pdf']})

---

"""

    md += "## Latest Tech Articles & News\n\n"

    for idx, a in enumerate(tech, 1):
        tags = " ".join([f"`{t}`" for t in a.get("tags", [])])
        info = f"{a['reading_time']} min read"
        if a.get("reactions", 0) > 0:
            info += f" | ❤️ {a['reactions']}"

        md += f"""
<details>
<summary><b>{idx}. {a['title']}</b></summary>

`{a['source']}` {tags}

**Published:** {a['published']} | {info}

_{a['description']}_

🔗 [Read More]({a['url']})

</details>

"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    main()
