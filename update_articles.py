import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote_plus
import re

ARXIV_API = "http://export.arxiv.org/api/query"
MAX_ARTICLES = 3

def fetch_arxiv():
    """Fetch latest AI research paper from arXiv"""
    query = "cat:cs.AI OR cat:cs.LG"
    params = {
        "search_query": query,
        "max_results": 1,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    url = ARXIV_API + "?" + "&".join(f"{k}={quote_plus(str(v))}" for k,v in params.items())
    resp = requests.get(url, headers={"User-Agent": "GitHub-Actions"}, timeout=10)
    resp.raise_for_status()
    
    root = ET.fromstring(resp.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", ns)
    
    if entry is None:
        return None
    
    title = entry.find("atom:title", ns).text.strip()
    summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")[:200] + "..."
    link = entry.find("atom:id", ns).text.strip()
    
    return {"title": title, "summary": summary, "url": link}

def fetch_tech_articles():
    """Fetch latest tech articles from Hacker News"""
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
                        'url': s.get('url'),
                        'score': s.get('score', 0)
                    })
            except:
                continue
    except:
        pass
    
    return articles

def update_readme():
    """Update the articles section in README.md"""
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Fetch content
    arxiv_paper = fetch_arxiv()
    tech_articles = fetch_tech_articles()
    
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    # Build new articles section
    new_section = f"""<!-- AUTO-UPDATE-START -->
# 📰 Latest AI & Tech Articles

_Last updated: {now}_

"""
    
    # Add arXiv paper
    if arxiv_paper:
        new_section += f"""### 🔬 Latest AI Research
**[{arxiv_paper['title']}]({arxiv_paper['url']})**  
_{arxiv_paper['summary']}_

"""
    
    # Add tech articles
    if tech_articles:
        new_section += "### 💻 Trending Tech\n"
        for idx, article in enumerate(tech_articles, 1):
            new_section += f"{idx}. **[{article['title']}]({article['url']})** (⬆️ {article['score']})\n"
    
    new_section += "<!-- AUTO-UPDATE-END -->"
    
    # Replace section using markers
    pattern = r'<!-- AUTO-UPDATE-START -->.*?<!-- AUTO-UPDATE-END -->'
    updated_content = re.sub(pattern, new_section, content, flags=re.DOTALL)
    
    # Write back
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    print("✔ README.md updated successfully")

if __name__ == "__main__":
    update_readme()
