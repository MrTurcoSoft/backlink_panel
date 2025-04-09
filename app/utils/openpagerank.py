# app/utils/openpagerank.py
import requests

API_KEY = "s8oso0wcwswogcswsg8o84wkc8gs44w08ks8w88w"  # Buraya kendi Open PageRank API anahtarını koy

def get_opr_score(domain):
    url = f"https://openpagerank.com/api/v1.0/getPageRank?domains%5B0%5D={domain}"
    headers = {
        "API-OPR": API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result and "response" in result and len(result["response"]) > 0:
            return result["response"][0].get("page_rank_integer")
        return None
    except Exception as e:
        print(f"[Open PageRank] Hata: {e}")
        return None
