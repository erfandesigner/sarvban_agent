
# =============================
# support/services/mongo.py
# =============================
from typing import List, Dict, Any
from django.conf import settings
from pymongo import MongoClient
import requests


_client = None

def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)
    return _client


def products_collection():
    client = get_client()
    db = client[settings.MONGO_DB]
    return db[settings.MONGO_PRODUCTS_COLLECTION]

def search_products_by_api(query: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
   
    url = "https://sarvban.com/keshton/api/market/search"

    if query.get("intent") == "buy":
        adType = "seller"
    elif query.get("intent") == "sell":
        adType = "buyer"
    else:
        adType = {"$in": ["buyer", "seller"]}

    if not query.get("product"):
        return []
    
    params ={
        "adType":adType,
        "key":query.get("product"),
        "page": limit
    }
    
    resp = requests.post(url, data=params, timeout=300)

    if resp.status_code == 200:
        return resp.json().get("results", [])
    
    return []


def search_products(query: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
    col = products_collection()

    # simple $text or regex search fallback
    if query.get("intent") == "buy":
        adType = "seller"
    elif query.get("intent") == "sell":
        adType = "buyer"
    else:
        adType = {"$in": ["buyer", "seller"]}

    pipeline = [
        {"$match": {
            "$or": [
                {"title": {"$regex": query["product"], "$options": "i"}},
                {"catPath.label": {"$regex": query["product"], "$options": "i"}},
                {"description": {"$regex": query["product"], "$options": "i"}},
            ],
            "adType": adType,
            "status": True,
            "deleted": False,
        }},
        {"$limit": limit}
        # {"$project": {"_id": 0}},
    ]
    return list(col.aggregate(pipeline))
