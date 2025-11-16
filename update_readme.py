import requests, xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote_plus

ARXIV_API = "http://export.arxiv.org/api/query"
CATEGORIES = ["cs.AI", "cs.LG"]

def fetch():
    query = " OR ".join(f"cat:{c}" for c in CATEGORIES)
    params = {
        "search_query": query,
        "max_results": 1,
        "start": 0,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    url = ARXIV_API + "?" + "&".join(f"{k}={quote_plus(str(v))}" for k,v in params.items())
    resp = requests.get(url, headers={"User-Agent":"GitHub-Actions"})
    resp.raise_for_status()
    return resp.text

def parse(xml_text):
    root = ET.fromstring(xml_text)
    ns = {"atom":"http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", ns)
    if entry is None: return None
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

def main():
    xml = fetch()
    p = parse(xml)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    banner = "https://svg-banners.vercel.app/api?type=luminance&text1=AI+Research+Digest&width=900&height=200"

    md = f"""
<p align="center"><img src="{banner}" /></p>

# 🧠 Latest AI Research (arXiv)
_Last updated: {now}_

### **[{p['title']}]({p['abs']})**

**Abstract:**  
{p['summary']}

📄 [Read Paper]({p['abs']})  
📘 [PDF]({p['pdf']})

---
"""
    with open("README.md","w",encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    main()
