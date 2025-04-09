# app/utils/scrapfly_search.py
from scrapfly import ScrapflyClient, ScrapeConfig
from bs4 import BeautifulSoup
from app.utils.comment_phrases import COMMENT_PHRASES

SCRAPFLY_KEY = "scp-live-5d45369f60d54fbfb7c2bad59a319695"
client = ScrapflyClient(key=SCRAPFLY_KEY)

def search_google(keyword, lang="de", page=0):
    start = page * 10
    phrase = COMMENT_PHRASES.get(lang, "")
    full_query = f'{keyword} "{phrase}"'  # İfadeyi tırnak içinde veriyoruz
    query = f"https://www.google.com/search?q={full_query}&hl={lang}&start={start}"

    result = client.scrape(ScrapeConfig(
        url=query,
        render_js=True,
        asp=True,
    ))

    if result.status_code == 200:
        return result.content
    else:
        print("Scrapfly Error:", result.status_code)
        return None
