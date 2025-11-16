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
    resp = requests.get(url, headers={"User-Agent":"GitHub-Actions"}, timeout=10)
    resp.raise_for_status()
    return resp.text

def parse_arxiv(xml_text):
    root = ET.fromstring(xml_text)
    ns = {"atom":"http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", ns)
    if entry is None: 
        return None
    title = entry.find("atom:title", ns).text.strip()
    summary = entry.find("atom:summary", ns).text.strip().replace("\n"," ")
    link = entry.find("atom:id", ns).text.strip()
    aid = link.split("/")[-1]
    return {
        "title": title,
        "summary": summary[:800]+"...",
        "abs": link,
        "pdf": f"https://arxiv.org/pdf/{aid}.pdf"
    }

def fetch_devto_articles():
    print("📡 Fetching Dev.to articles...")
    articles = []
    try:
        url = "https://dev.to/api/articles?per_page=10&top=7"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✔ Found {len(data)} articles")
            
            for article in data[:MAX_ARTICLES]:
                articles.append({
                    'title': article.get('title', 'Untitled'),
                    'description': article.get('description', article.get('title', ''))[:200],
                    'url': article.get('url', '#'),
                    'published': article.get('published_at', '')[:10],
                    'tags': article.get('tag_list', [])[:3],
                    'reactions': article.get('public_reactions_count', 0),
                    'reading_time': article.get('reading_time_minutes', 5),
                    'source': 'Dev.to'
                })
    except Exception as e:
        print(f"   ✗ Dev.to error: {e}")
    
    return articles

def fetch_hackernews():
    print("📡 Fetching Hacker News...")
    articles = []
    try:
        response = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        )
        
        if response.status_code == 200:
            story_ids = response.json()[:10]
            
            for story_id in story_ids[:MAX_ARTICLES]:
                try:
                    story_response = requests.get(
                        f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                        timeout=5
                    )
                    
                    if story_response.status_code == 200:
                        story = story_response.json()
                        
                        if story.get('type') == 'story' and story.get('url'):
                            articles.append({
                                'title': story.get('title', 'Untitled'),
                                'description': story.get('title', '')[:200],
                                'url': story.get('url', '#'),
                                'published': datetime.fromtimestamp(story.get('time', 0)).strftime('%Y-%m-%d'),
                                'tags': ['tech', 'news'],
                                'reactions': story.get('score', 0),
                                'reading_time': 5,
                                'source': 'Hacker News'
                            })
                            
                            if len(articles) >= MAX_ARTICLES:
                                break
                except:
                    continue
                    
            print(f"   ✔ Found {len(articles)} stories")
    except Exception as e:
        print(f"   ✗ Hacker News error: {e}")
    
    return articles

def fetch_medium_rss():
    print("📡 Fetching Medium RSS...")
    articles = []
    try:
        feed = feedparser.parse("https://medium.com/feed/tag/technology")
        
        for entry in feed.entries[:MAX_ARTICLES]:
            articles.append({
                'title': entry.get('title', 'Untitled'),
                'description': entry.get('summary', '')[:200].replace('<p>', '').replace('</p>', ''),
                'url': entry.get('link', '#'),
                'published': entry.get('published', '')[:10],
                'tags': ['tech'],
                'reactions': 0,
                'reading_time': 5,
                'source': 'Medium'
            })
        
        print(f"   ✔ Found {len(articles)} articles")
    except Exception as e:
        print(f"   ✗ Medium error: {e}")
    
    return articles

def get_tech_articles():
    all_sources = [
        fetch_devto_articles,
        fetch_hackernews,
        fetch_medium_rss
    ]
    
    all_articles = []
    
    for fetch_func in all_sources:
        try:
            articles = fetch_func()
            if articles:
                all_articles.extend(articles)
                if len(all_articles) >= MAX_ARTICLES:
                    break
        except:
            continue
    
    seen_titles = set()
    unique_articles = []
    
    for article in all_articles:
        if article['title'] not in seen_titles:
            seen_titles.add(article['title'])
            unique_articles.append(article)
            
            if len(unique_articles) >= MAX_ARTICLES:
                break
    
    return unique_articles

def main():
    print("\n🚀 Generating README...\n")
    
    # Fetch arXiv paper
    xml = fetch_arxiv()
    arxiv_paper = parse_arxiv(xml)
    
    # Fetch tech articles
    tech_articles = get_tech_articles()
    
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    banner = "https://svg-banners.vercel.app/api?type=luminance&text1=AI+Research+Digest&width=900&height=200"
    
    md = f"""<p align="center"><img src="{banner}" /></p>

# 🧠 Latest AI Research (arXiv)

_Last updated: {now}_

"""
    
    if arxiv_paper:
        md += f"""### **[{arxiv_paper['title']}]({arxiv_paper['abs']})**

**Abstract:**  
{arxiv_paper['summary']}

📄 [Read Paper]({arxiv_paper['abs']})  
📘 [PDF]({arxiv_paper['pdf']})

---

"""
    
    # Add tech articles section
    md += """## 📚 Latest Tech Articles & News

> 🔄 Auto-updated every 12 hours

"""
    
    if tech_articles:
        for idx, article in enumerate(tech_articles, 1):
            source_badge = f"`{article['source']}`"
            tag_badges = " ".join([f"`{tag}`" for tag in article.get('tags', [])[:3]])
            
            reactions_info = ""
            if article.get('reading_time', 0) > 0:
                reactions_info = f"⏱️ {article['reading_time']} min read"
            if article.get('reactions', 0) > 0:
                if reactions_info:
                    reactions_info += " | "
                reactions_info += f"{'⭐' if article['source'] == 'GitHub' else '❤️'} {article['reactions']}"
            
            md += f"""
<details>
<summary><b>{idx}. {article['title']}</b></summary>

{source_badge} {tag_badges}

**Published:** {article['published']} {('| ' + reactions_info) if reactions_info else ''}

_{article['description']}_

🔗 [Read More]({article['url']})

</details>

"""
    else:
        md += "\n> ⚠️ No articles available at this time.\n\n"
    
    md += "\n---\n"
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md)
    
    print("\n✅ README.md generated successfully!\n")

if __name__ == "__main__":
    main()
