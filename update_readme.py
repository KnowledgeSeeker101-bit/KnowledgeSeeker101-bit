import requests
import xml.etree.ElementTree as ET
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

ARXIV_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "stat.ML"]
MAX_ARTICLES = 5

def fetch_arxiv_articles():
    query = " OR ".join(f"cat:{c}" for c in ARXIV_CATEGORIES)
    params = {
        "search_query": query,
        "max_results": MAX_ARTICLES,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    url = "http://export.arxiv.org/api/query?" + "&".join(
        f"{k}={quote_plus(str(v))}" for k, v in params.items()
    )
    
    try:
        response = requests.get(url, headers={"User-Agent": "GitHub-Actions"}, timeout=10)
        response.raise_for_status()
        return parse_arxiv_response(response.text)
    except Exception as e:
        print(f"Error fetching arXiv: {e}")
        return []

def parse_arxiv_response(xml_text):
    articles = []
    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    
    for entry in root.findall("atom:entry", ns):
        try:
            title_elem = entry.find("atom:title", ns)
            summary_elem = entry.find("atom:summary", ns)
            link_elem = entry.find("atom:id", ns)
            published_elem = entry.find("atom:published", ns)
            
            if not all([title_elem, summary_elem, link_elem, published_elem]):
                continue
                
            title = title_elem.text.strip().replace("\n", " ")
            summary = summary_elem.text.strip().replace("\n", " ")
            link = link_elem.text.strip()
            arxiv_id = link.split("/")[-1]
            published = published_elem.text[:10]
            
            categories = [cat.attrib.get("term", "") for cat in entry.findall("atom:category", ns)]
            
            articles.append({
                "title": title,
                "summary": summary[:250] + "..." if len(summary) > 250 else summary,
                "link": link,
                "pdf": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                "published": published,
                "categories": categories[:3]
            })
        except Exception as e:
            print(f"Error parsing entry: {e}")
            continue
    
    return articles

def generate_readme():
    config = PROFILE_CONFIG
    articles = fetch_arxiv_articles()
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

## 📚 Latest AI Research Feed

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12&height=100&section=header&text=Fresh%20AI%20Articles&fontSize=35&fontColor=fff&animation=twinkling" width="100%"/>
</div>

> 🔄 Auto-updated every 12 hours | 📅 Last update: **{now}**

'''
    
    if articles:
        for idx, article in enumerate(articles, 1):
            category_badges = " ".join([
                f'<img src="https://img.shields.io/badge/{cat.replace("-", "--")}-blue?style=flat-square" />'
                for cat in article["categories"]
            ])
            
            readme += f'''
<details open>
<summary><b>📄 {idx}. {article["title"]}</b></summary>

<br/>

{category_badges}

**Published:** {article["published"]}

**Abstract:**  
_{article["summary"]}_

<div align="center">

[![Read Paper](https://img.shields.io/badge/Read_Paper-arXiv-B31B1B?style=for-the-badge&logo=arxiv&logoColor=white)]({article["link"]})
[![Download PDF](https://img.shields.io/badge/Download_PDF-6366F1?style=for-the-badge&logo=adobe-acrobat-reader&logoColor=white)]({article["pdf"]})

</div>

</details>

'''
    else:
        readme += "\n> ⚠️ No articles available\n\n"
    
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
