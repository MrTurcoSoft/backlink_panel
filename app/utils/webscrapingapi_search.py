import requests

def find_comment_enabled_sites(keyword, lang="en", page_limit=5):
    API_KEY = "vJDZTiyfCyzC2hO44ZsEvVP4XSIA5OWi"
    BASE_URL = "https://serpapi.webscrapingapi.com/v2"
    COMMENT_PHRASES = {
        "en": "leave a comment",
        "de": "Kommentar hinterlassen",
        "fr": "laisser un commentaire",
        "es": "deja un comentario",
        "it": "lascia un commento",
        "tr": "yorum yap",
    }
    query_phrase = COMMENT_PHRASES.get(lang, "leave a comment")
    query = f'"{keyword}" inurl:blog inurl:comments "{query_phrase}"'

    all_sites = []

    for page in range(page_limit):
        params = {
            "engine": "google",
            "api_key": API_KEY,
            "q": query,
            "hl": lang,
            "gl": lang,
            "num": 10,
            "start": page * 10
        }

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if "organic" in data:
                for item in data["organic"]:
                    all_sites.append({
                        "url": item.get("link"),
                        "title": item.get("title"),
                        "snippet": item.get("snippet", "")
                    })

        except Exception as e:
            print(f"🔴 API Hatası (sayfa {page+1}): {e}")
            break

    return all_sites
