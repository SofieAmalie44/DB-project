from django.http import JsonResponse
from django.views import View
from bson import ObjectId
from pymongo import MongoClient
import json

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
items_collection = db["item"]

def fix_id(doc):
    """Convert ObjectId → string"""
    doc["_id"] = str(doc["_id"])
    return doc

@method_decorator(csrf_exempt, name='dispatch')
class MongoItemList(View):
    """GET all items + CREATE new item"""

    def get(self, request):
        items = [fix_id(doc) for doc in items_collection.find()]
        return JsonResponse(items, safe=False)

    def post(self, request):
        body = json.loads(request.body)

        # Insert into MongoDB
        result = items_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return JsonResponse(body, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class MongoItemDetail(View):
    """GET one item + UPDATE + DELETE"""

    def get(self, request, item_id):
        doc = items_collection.find_one({"id": int(item_id)})
        if not doc:
            return JsonResponse({"error": "Item not found"}, status=404)
        return JsonResponse(fix_id(doc))

    def put(self, request, item_id):
        body = json.loads(request.body)

        result = items_collection.update_one(
            {"id": int(item_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return JsonResponse({"error": "Item not found"}, status=404)

        updated = items_collection.find_one({"id": int(item_id)})
        return JsonResponse(fix_id(updated))

    def delete(self, request, item_id):
        result = items_collection.delete_one({"id": int(item_id)})

        if result.deleted_count == 0:
            return JsonResponse({"error": "Item not found"}, status=404)

        return JsonResponse({"status": "Item deleted"})
