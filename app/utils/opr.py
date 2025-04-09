# app/utils/opr.py
import requests

def get_page_rank(domain):
    api_key = "s8oso0wcwswogcswsg8o84wkc8gs44w08ks8w88w"  # https://www.domcop.com/openpagerank/ adresinden ücretsiz alabilirsin

    headers = {
        "API-OPR": api_key
    }

    try:
        response = requests.get(
            f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}",
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        return result["response"][0].get("page_rank_decimal", None)
    except Exception as e:
        print(f"[OPR API] Hata: {e}")
        return None
