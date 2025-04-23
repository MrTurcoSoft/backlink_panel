# app/utils/openpagerank.py
import requests

API_KEY = "s8oso0wcwswogcswsg8o84wkc8gs44w08ks8w88w"  # Buraya kendi Open PageRank API anahtarını koy

def get_opr_score(domain):
    """Open PageRank API'den PageRank değerini alır."""
    url = f"https://openpagerank.com/api/v1.0/getPageRank?domains%5B0%5D={domain}"
    headers = {"API-OPR": API_KEY}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        if "response" in result and result["response"]:
            return result["response"][0].get("page_rank_integer")
        logging.warning("PageRank değeri alınamadı.")
        return None
    except requests.RequestException as e:
        logging.error(f"[Open PageRank] Hata: {e}")
        return None