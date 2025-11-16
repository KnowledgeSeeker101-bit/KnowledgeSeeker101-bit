import requests
from datetime import datetime
from urllib.parse import quote_plus
import os

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

# Dev.to tags to fetch articles from
DEVTO_TAGS = ["ai", "machinelearning", "python", "datascience", "deeplearning"]
MAX_ARTICLES = 5

def fetch_devto_articles():
    # Fetch latest tech articles from Dev.to API
    articles = []
    
    try:
        # Fetch articles for each tag
        for tag in DEVTO_TAGS[:2]:  # Limit to 2 tags to avoid rate limits
            url = f"https://dev.to/api/articles?tag={tag}&per_page=3&top=7"
            response = requests.get(
                url,
                headers={
                    "User-Agent": "GitHub-Actions",
                    "Accept": "application/json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                for article in data:
                    if len(articles) >= MAX_ARTICLES:
                        break
                    
                    # Avoid duplicates
                    if not any(a['id'] == article['id'] for a in articles):
                        articles.append({
                            'id': article['id'],
                            'title': article['title'],
                            'description': article['description'] or article['title'],
                            'url': article['url'],
                            'published': article['published_at'][:10],
                            'tags': article['tag_list'][:3],
                            'reading_time': article.get('reading_time_minutes', 5),
                            'reactions': article.get('public_reactions_count', 0)
                        })
            
            if len(articles) >= MAX_ARTICLES:
                break
                
    except Exception as e:
        print(f"Error fetching Dev.to articles: {e}")
    
    # Sort by reactions/popularity
    articles.sort(key=lambda x: x['reactions'], reverse=True)
    return articles[:MAX_ARTICLES]

def fetch_github_trending():
    # Fetch trending repositories as fallback
    try:
        url = "https://api.github.com/search/repositories?q=stars:>1000+language:python&sort=stars&order=desc&per_page=3"
        response = requests.get(
            url,
            headers={
                "User-Agent": "GitHub-Actions",
                "Accept": "application/vnd.github.v3+json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            repos = []
            for repo in data.get('items', [])[:3]:
                repos.append({
                    'title': repo['full_name'],
                    'description': repo['description'] or 'No description',
                    'url': repo['html_url'],
                    'stars': repo['stargazers_count'],
                    'language': repo['language']
                })
            return repos
    except Exception as e:
        print(f"Error fetching GitHub trending: {e}")
    
    return []

def generate_readme():
    config = PROFILE_CONFIG
    articles = fetch_devto_articles()
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

## 📚 Latest Tech Articles

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12&height=100&section=header&text=Fresh%20Tech%20Reads&fontSize=35&fontColor=fff&animation=twinkling" width="100%"/>
</div>

> 🔄 Auto-updated every 12 hours | 📅 Last update: **{now}**

'''
    
    if articles:
        for idx, article in enumerate(articles, 1):
            tag_badges = " ".join([
                f'<img src="https://img.shields.io/badge/{tag.replace("-", "--")}-blue?style=flat-square" />'
                for tag in article["tags"]
            ])
            
            readme += f'''
<details open>
<summary><b>📄 {idx}. {article["title"]}</b></summary>

<br/>

{tag_badges}

**Published:** {article["published"]} | ⏱️ {article["reading_time"]} min read | ❤️ {article["reactions"]} reactions

**Description:**  
_{article["description"]}_

<div align="center">

[![Read Article](https://img.shields.io/badge/Read_on_Dev.to-0A0A0A?style=for-the-badge&logo=dev.to&logoColor=white)]({article["url"]})

</div>

</details>

'''
    else:
        readme += "\n> ⚠️ No articles available. Showing GitHub trending projects:\n\n"
        
        # Fallback to GitHub trending
        trending = fetch_github_trending()
        if trending:
            for idx, repo in enumerate(trending, 1):
                readme += f'''
**{idx}. [{repo["title"]}]({repo["url"]})**  
{repo["description"]}  
⭐ {repo["stars"]:,} stars | 💻 {repo["language"]}

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
    print("🎨 Generating README...")
    readme_content = generate_readme()
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ README.md generated!")

if __name__ == "__main__":
    main()
