import requests
import json

from app.utils.comment_phrases import COMMENT_PHRASES

# Ülke uzantılarını eşle
DOMAIN_EXTENSIONS = {
    "de": ".de",
    "en": ".com",
    "fr": ".fr",
    "es": ".es",
    "it": ".it",
    "tr": ".com.tr"
}

def find_comment_enabled_sites(keyword, lang="en", page_limit=5):
    API_KEY = "1e3e368bcad71f81d643200611f85e732fbefa04"
    url = "https://google.serper.dev/search"

    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    phrase = COMMENT_PHRASES.get(lang, "leave a comment")
    domain = DOMAIN_EXTENSIONS.get(lang, ".com")

    query = f'"{keyword}" inurl:blog | inurl:post | inurl:comments "{phrase}" site:{domain}'

    all_sites = []

    for page in range(page_limit):
        payload = {
            "q": query,
            "gl": lang,
            "autocorrect": True,
            "hl": lang,
            "page": page + 1,
            "type": "search"
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            result = response.json()

            if "organic" in result:
                for item in result["organic"]:
                    all_sites.append({
                        "url": item.get("link"),
                        "title": item.get("title"),
                        "snippet": item.get("snippet", "")
                    })

        except Exception as e:
            print(f"🔴 Serper API cevabı:\n{response.text}")  # JSON olmayan yanıtı göster
            raise
            # print(f"[Serper API] Hata: {e}")
            # break

    return all_sites