# app/utils/moz.py
import requests

def get_domain_authority(domain):
    access_token = "bW96c2NhcGUtT1lxSmZsR3l5TjpTTjhQbDVFNEN6Zk5vTnczcUhYNDBENWlUam9jSDZaQQ=="  # 👈 kendi Access Token'ını buraya yaz
    endpoint = "https://lsapi.seomoz.com/v2/url_metrics"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "targets": [f"https://{domain}"]
    }

    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        result_data = result.get("results", [{}])[0]
        return {
            "domain_authority": result_data.get("domain_authority", None),
            "page_authority": result_data.get("page_authority", None)
        }
    except Exception as e:
        print(f"[Moz API] Hata: {e}")
        return {
            "domain_authority": None,
            "page_authority": None
        }
