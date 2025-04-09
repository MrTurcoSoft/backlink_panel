# app/google_scraper.py
from serpapi import GoogleSearch

API_KEY_1 = "ceb53bf26a6b1d79ff7c23d57f149ff0cb777a4387af9bf8aa6bbfd981f3e787" ##atilturk@gmail
API_KEY_2 = "4092de3e35f6025765386df03bfdb6fa8b0508147823ff88ee9e6b122e7bd947" ##Milasevent@gmail
API_KEY_3 = "a711c8b2bc47a5cc06aa53955b7426c1e0b48dcc64cf60fbc6225ad343a858a8" ##byturcoyazilim@gmail

COMMENT_PHRASES = {
    "de": "Kommentar hinterlassen",
    "en": "leave a comment",
    "fr": "laisser un commentaire",
    "es": "deja un comentario",
    "it": "lascia un commento",
    "tr": "yorum yap"
}

def find_comment_enabled_sites(keyword, pages, lang="de"):
    results_list = []

    comment_phrase = COMMENT_PHRASES.get(lang, "leave a comment")
    search_query = f'{keyword} "{comment_phrase}" site:.{lang}'

    for start in range(0, pages * 10, 10):
        params = {
            "engine": "google",
            "q": search_query,
            "hl": lang,
            "gl": lang,
            "start": start,
            "api_key": API_KEY_2
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        if "organic_results" in results:
            for result in results["organic_results"]:
                link = result.get("link")
                if link:
                    results_list.append(link)

    return results_list

# app/utils/scrapfly_search.py
from scrapfly import ScrapflyClient, ScrapeConfig
import os

SCRAPFLY_KEY = "YOUR_SCRAPFLY_API_KEY"  # 🔐 API anahtarını buraya koy

client = ScrapflyClient(key=SCRAPFLY_KEY)

def search_google(keyword, lang="de", page=0):
    start = page * 10
    query = f"https://www.google.com/search?q={keyword}&hl={lang}&start={start}"

    result = client.scrape(ScrapeConfig(
        url=query,
        render_js=True,
        asp=True,
    ))

    if result.status_code == 200:
        html = result.content
        return html  # burada parse işlemi yapılabilir
    else:
        print("Scrapfly Error:", result.status_code)
        return None
