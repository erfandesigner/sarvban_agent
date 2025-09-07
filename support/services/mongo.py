
# =============================
# support/services/mongo.py
# =============================
from typing import List, Dict, Any
from django.conf import settings
from pymongo import MongoClient

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


def search_products(query: object, limit: int = 5) -> List[Dict[str, Any]]:
    col = products_collection()
    # simple $text or regex search fallback
    pipeline = [
        {"$match": {"$or": [
            {"title": {"$regex": query["product"], "$options": "i"}},
            {"catPath.label": {"$regex": query["product"], "$options": "i"}},
            {"description": {"$regex": query["product"], "$options": "i"}},
        ]},"adType": query["intent"]},

        {"$limit": limit},
        {"$project": {"_id": 0}},
    ]
    return list(col.aggregate(pipeline))
