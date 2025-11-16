import requests
from datetime import datetime
from urllib.parse import quote_plus
import os
import feedparser
import json

# ========================================
# CUSTOMIZE YOUR PROFILE HERE!
# ========================================
PROFILE_CONFIG = {
    "name": "Your Name",
    "tagline": "AI Researcher | ML Engineer | Open Source Enthusiast",
    "interests": [
        "Artificial Intelligence",
        "Deep Learning", 
        "Natural Language Processing",
        "Computer Vision",
        "MLOps"
    ],
    "github_user": os.getenv("GITHUB_USER", "yourusername"),
    "social": {
        "linkedin": "your-linkedin",
        "twitter": "your-twitter",
        "website": "https://yourwebsite.com"
    }
}

MAX_ARTICLES = 5

def fetch_devto_articles():
    # Fetch from Dev.to - NO AUTH REQUIRED
    print("📡 Fetching from Dev.to...")
    articles = []
    
    try:
        # Use latest articles endpoint with top articles
        url = "https://dev.to/api/articles?per_page=10&top=7"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        print(f"   Dev.to status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} articles")
            
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
        else:
            print(f"   Dev.to returned {response.status_code}")
            
    except Exception as e:
        print(f"   Error with Dev.to: {e}")
    
    return articles

def fetch_hackernews_articles():
    # Fetch from Hacker News API
    print("📡 Fetching from Hacker News...")
    articles = []
    
    try:
        # Get top stories
        response = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        )
        
        if response.status_code == 200:
            story_ids = response.json()[:10]
            print(f"   Found {len(story_ids)} top stories")
            
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
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"   Error with Hacker News: {e}")
    
    return articles

def fetch_github_trending():
    # Fetch trending GitHub repositories
    print("📡 Fetching GitHub Trending...")
    articles = []
    
    try:
        url = "https://api.github.com/search/repositories"
        params = {
            "q": "stars:>1000 language:python created:>2024-01-01",
            "sort": "stars",
            "order": "desc",
            "per_page": MAX_ARTICLES
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"   GitHub status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            repos = data.get('items', [])
            print(f"   Found {len(repos)} repositories")
            
            for repo in repos[:MAX_ARTICLES]:
                articles.append({
                    'title': repo.get('full_name', 'Untitled'),
                    'description': repo.get('description', 'No description')[:200],
                    'url': repo.get('html_url', '#'),
                    'published': repo.get('created_at', '')[:10],
                    'tags': [repo.get('language', 'Unknown')],
                    'reactions': repo.get('stargazers_count', 0),
                    'reading_time': 0,
                    'source': 'GitHub'
                })
                
    except Exception as e:
        print(f"   Error with GitHub: {e}")
    
    return articles

def fetch_medium_tech_feed():
    # Fetch from Medium's public RSS feed
    print("📡 Fetching from Medium RSS...")
    articles = []
    
    try:
        # Medium's technology tag RSS feed
        feed_url = "https://medium.com/feed/tag/technology"
        feed = feedparser.parse(feed_url)
        print(f"   Found {len(feed.entries)} Medium articles")
        
        for entry in feed.entries[:MAX_ARTICLES]:
            articles.append({
                'title': entry.get('title', 'Untitled'),
                'description': entry.get('summary', '')[:200].replace('<p>', '').replace('</p>', ''),
                'url': entry.get('link', '#'),
                'published': entry.get('published', '')[:10],
                'tags': ['tech', 'medium'],
                'reactions': 0,
                'reading_time': 5,
                'source': 'Medium'
            })
            
    except Exception as e:
        print(f"   Error with Medium: {e}")
    
    return articles

def get_articles():
    # Try multiple sources and return the first successful one
    print("\n🔍 Fetching articles from multiple sources...\n")
    
    all_sources = [
        fetch_devto_articles,
        fetch_hackernews_articles,
        fetch_github_trending,
        fetch_medium_tech_feed
    ]
    
    all_articles = []
    
    for fetch_func in all_sources:
        try:
            articles = fetch_func()
            if articles:
                all_articles.extend(articles)
                print(f"✅ Got {len(articles)} articles from {articles[0]['source']}\n")
                if len(all_articles) >= MAX_ARTICLES:
                    break
        except Exception as e:
            print(f"❌ Source failed: {e}\n")
            continue
    
    # Return unique articles (based on title)
    seen_titles = set()
    unique_articles = []
    
    for article in all_articles:
        if article['title'] not in seen_titles:
            seen_titles.add(article['title'])
            unique_articles.append(article)
            
            if len(unique_articles) >= MAX_ARTICLES:
                break
    
    print(f"\n📊 Total unique articles: {len(unique_articles)}\n")
    return unique_articles

def generate_readme():
    config = PROFILE_CONFIG
    articles = get_articles()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    user = config["github_user"]
    
    readme = f'''<div align="center">

# 👋 Hi, I'm {config["name"]}

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=28&duration=3000&pause=1000&color=6366F1&center=true&vCenter=true&width=600&lines={quote_plus(config["tagline"])}" alt="Typing SVG" />

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/{config["social"].get("linkedin", "")})
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/{config["social"].get("twitter", "")})
[![Website](https://img.shields.io/badge/Website-FF5722?style=for-the-badge&logo=google-chrome&logoColor=white)]({config["social"].get("website", "#")})

</div>

---

## 🚀 About Me

<img align="right" width="400" src="https://github-readme-stats.vercel.app/api?username={user}&show_icons=true&theme=tokyonight&hide_border=true&bg_color=0D1117&title_color=6366F1&icon_color=6366F1&text_color=C9D1D9" />

I'm passionate about AI and machine learning:

'''
    
    interest_emojis = ["🤖", "🧠", "💬", "👁️", "⚙️", "📊", "🔬", "💡"]
    for i, interest in enumerate(config["interests"]):
        emoji = interest_emojis[i % len(interest_emojis)]
        readme += f"- {emoji} **{interest}**\n"
    
    readme += f'''

<br clear="right"/>

---

## 📊 GitHub Statistics

<div align="center">
  <img height="180em" src="https://github-readme-stats.vercel.app/api/top-langs/?username={user}&layout=compact&theme=tokyonight&hide_border=true&bg_color=0D1117&title_color=6366F1&text_color=C9D1D9&langs_count=8"/>
  <img height="180em" src="https://github-readme-streak-stats.herokuapp.com/?user={user}&theme=tokyonight&hide_border=true&background=0D1117&ring=6366F1&fire=6366F1&currStreakLabel=6366F1"/>
</div>

---

## 📚 Latest Tech Articles & News

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12&height=100&section=header&text=Fresh%20Tech%20Content&fontSize=35&fontColor=fff&animation=twinkling" width="100%"/>
</div>

> 🔄 Auto-updated every 12 hours | 📅 Last update: **{now}**

'''
    
    if articles:
        for idx, article in enumerate(articles, 1):
            source_badge = f'<img src="https://img.shields.io/badge/Source-{article["source"].replace(" ", "_")}-green?style=flat-square" />'
            
            tag_badges = " ".join([
                f'<img src="https://img.shields.io/badge/{tag.replace("-", "--").replace(" ", "_")}-blue?style=flat-square" />'
                for tag in article.get("tags", [])
            ])
            
            reactions_info = ""
            if article.get("reading_time", 0) > 0:
                reactions_info = f"⏱️ {article['reading_time']} min read | "
            if article.get("reactions", 0) > 0:
                reactions_info += f"{'⭐' if article['source'] == 'GitHub' else '❤️'} {article['reactions']} "
            
            readme += f'''
<details open>
<summary><b>📄 {idx}. {article["title"]}</b></summary>

<br/>

{source_badge} {tag_badges}

**Published:** {article["published"]} {("| " + reactions_info) if reactions_info else ""}

**Description:**  
_{article["description"]}_

<div align="center">

[![Read More](https://img.shields.io/badge/Read_More-6366F1?style=for-the-badge&logo=google-chrome&logoColor=white)]({article["url"]})

</div>

</details>

'''
    else:
        readme += '''
> ⚠️ Unable to fetch articles at this time. Please check back later!

'''
    
    readme += f'''
---

## 🛠️ Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

## 📈 Activity Graph

<div align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username={user}&theme=tokyo-night&hide_border=true&bg_color=0D1117&color=6366F1&line=6366F1&point=C9D1D9" width="100%"/>
</div>

---

<div align="center">

### 💬 Let's Connect!

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12&height=100&section=footer" width="100%"/>

**⭐️ From [{user}](https://github.com/{user})**

</div>
'''
    
    return readme

def main():
    print("\n" + "="*50)
    print("🎨 Generating README with Tech Articles")
    print("="*50 + "\n")
    
    readme_content = generate_readme()
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("\n" + "="*50)
    print("✅ README.md generated successfully!")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
