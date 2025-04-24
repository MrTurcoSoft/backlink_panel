import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from app.utils.comment_phrases import COMMENT_PHRASES

def find_comment_enabled_sites(keyword, lang="en", page_limit=5):
    proxy = {
        "http": "http://brd-customer-hl_6242f3d7-zone-serp_api1:ui8v7r9gnexh@brd.superproxy.io:33335",
        "https": "http://brd-customer-hl_6242f3d7-zone-serp_api1:ui8v7r9gnexh@brd.superproxy.io:33335",
    }

    domain = {
        "de": "google.de", "fr": "google.fr", "tr": "google.com.tr",
        "en": "google.com", "es": "google.es", "it": "google.it"
    }.get(lang, "google.com")

    phrase = COMMENT_PHRASES.get(lang, "leave a comment")
    query = f'"{keyword}" inurl:blog | inurl:post | inurl:comments "{phrase}"'

    all_sites = []

    for page in range(page_limit):
        start = page * 10
        url = f"https://{domain}/search?q={quote_plus(query)}&hl={lang}&start={start}"

        try:
            response = requests.get(url, proxies=proxy, timeout=30)
            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            for g in soup.select("div.g"):
                link = g.find("a", href=True)
                title = g.find("h3")
                snippet = g.find("span", class_="aCOpRe")

                if link and title:
                    all_sites.append({
                        "url": link["href"],
                        "title": title.get_text(strip=True),
                        "snippet": snippet.get_text(strip=True) if snippet else ""
                    })

        except Exception as e:
            print(f"🔴 Bright Data hatası: {e}")

    return all_sites
