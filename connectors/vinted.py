from curl_cffi import requests

def search_vinted(query, per_page=20):
    url = "https://www.vinted.fr/api/v2/catalog/items"
    params = {
        "search_text": query,
        "per_page": per_page,
        "page": 1
    }
    
    try:
        # impersonate="chrome120" permet de contourner la détection anti-bot de Vinted
        response = requests.get(url, params=params, impersonate="chrome120", timeout=10)
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
