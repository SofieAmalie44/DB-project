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
characters_collection = db["character"]


# Helper to convert ObjectId to string
def fix_id(document):
    document["_id"] = str(document["_id"])
    return document

@method_decorator(csrf_exempt, name='dispatch')
class MongoCharacterList(View):
    def get(self, request):
        """Get all characters from MongoDB"""
        data = [fix_id(doc) for doc in characters_collection.find()]
        return JsonResponse(data, safe=False)

    def post(self, request):
        """Create a new character in MongoDB"""
        body = json.loads(request.body)

        result = characters_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)
        return JsonResponse(body, status=201)
    
@method_decorator(csrf_exempt, name='dispatch')
class MongoCharacterDetail(View):
    def get(self, request, char_id):
        """Get a single character"""
        doc = characters_collection.find_one({"id": int(char_id)})

        if not doc:
            return JsonResponse({"error": "Character not found"}, status=404)

        return JsonResponse(fix_id(doc))

    def put(self, request, char_id):
        """Update a character"""
        body = json.loads(request.body)

        result = characters_collection.update_one(
            {"id": int(char_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return JsonResponse({"error": "Character not found"}, status=404)

        updated = characters_collection.find_one({"id": int(char_id)})
        return JsonResponse(fix_id(updated))

    def delete(self, request, char_id):
        """Delete a character"""
        result = characters_collection.delete_one({"id": int(char_id)})

        if result.deleted_count == 0:
            return JsonResponse({"error": "Character not found"}, status=404)

        return JsonResponse({"status": "Character deleted"})
