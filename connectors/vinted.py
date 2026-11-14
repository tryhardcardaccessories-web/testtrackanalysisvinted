from curl_cffi import requests

def search_vinted(query, per_page=20):
    session = requests.Session()
    
    # 1. Établir une session valide en récupérant la page d'accueil avec les cookies français
    try:
        session.get("https://www.vinted.fr/", impersonate="chrome120", timeout=10)
    except Exception:
        pass

    url = "https://www.vinted.fr/api/v2/catalog/items"
    params = {
        "search_text": query,
        "per_page": per_page,
        "page": 1
    }
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.vinted.fr/",
        "Accept-Language": "fr-FR,fr;q=0.9"
    }
    
    try:
        response = session.get(url, params=params, headers=headers, impersonate="chrome120", timeout=10)
        if response.status_code != 200:
            return []
        
        items = response.json().get("items", [])
        formatted_listings = []
        for item in items:
            price_info = item.get("price", {})
            photo = item.get("photo", {})
            
            formatted_listings.append({
                "listing_id": str(item.get("id")),
                "title": item.get("title"),
                "price": float(price_info.get("amount", 0)) if isinstance(price_info, dict) else float(price_info or 0),
                "condition": item.get("status"),
                "shipping_cost": None,
                "date_published": None,
                "url": item.get("url"),
                "image_url": photo.get("url") if isinstance(photo, dict) else None,
                "source": "vinted_direct"
            })
        return formatted_listings
    except Exception:
        return []
