import requests
import json

from app.utils.comment_phrases import COMMENT_PHRASES

# Ülke uzantılarını eşle
DOMAIN_EXTENSIONS = {
    "de": "de",
    "en": "en",
    "fr": "fr",
    "es": "es",
    "it": "it",
    "tr": "tr"
}

def find_comment_enabled_sites(keyword, lang="en", page_limit=10):
    API_KEY = "1e3e368bcad71f81d643200611f85e732fbefa04"
    url = "https://google.serper.dev/search"

    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    phrase = COMMENT_PHRASES.get(lang, "leave a comment")
    domain = DOMAIN_EXTENSIONS.get(lang, ".com")
    num = page_limit * 10
    query = f'"{keyword}" inurl:blog | inurl:post | inurl:comments "{phrase}"'

    payload = {
        "q": query,
        "gl": domain,
        "autocorrect": True,
        "hl": domain,
        "num": num   # 10 sonuç x sayfa
    }

    all_sites = []

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if "organic" in result:
            organic_results = result["organic"]
            for i in range(page_limit):
                print(f"\n🟢 {i+1}. sayfa taranıyor...\n")
                for j in range(10):
                    idx = i * 10 + j
                    if idx < len(organic_results):
                        item = organic_results[idx]
                        print(f"🔗 {item.get('link')}")
                        all_sites.append({
                            "url": item.get("link"),
                            "title": item.get("title", ""),
                            "snippet": item.get("snippet", "")
                        })

    except Exception as e:
        print(f"🔴 Serper API cevabı:\n{response.text}")
        raise

    return all_sites

