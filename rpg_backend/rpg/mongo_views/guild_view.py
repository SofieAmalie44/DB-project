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
guild_collection = db["guild"]


def fix_id(doc):
    """Convert ObjectId to string for JSON output"""
    doc["_id"] = str(doc["_id"])
    return doc


@method_decorator(csrf_exempt, name="dispatch")
class MongoGuildList(View):
    """GET all guilds / POST create a new guild"""

    def get(self, request):
        guilds = [fix_id(doc) for doc in guild_collection.find()]
        return JsonResponse(guilds, safe=False)

    def post(self, request):
        body = json.loads(request.body)

        result = guild_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return JsonResponse(body, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class MongoGuildDetail(View):
    """GET one guild / PUT update / DELETE"""

    def get(self, request, guild_id):
        doc = guild_collection.find_one({"id": int(guild_id)})
        if not doc:
            return JsonResponse({"error": "Guild not found"}, status=404)
        return JsonResponse(fix_id(doc))

    def put(self, request, guild_id):
        body = json.loads(request.body)

        result = guild_collection.update_one(
            {"id": int(guild_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return JsonResponse({"error": "Guild not found"}, status=404)

        updated = guild_collection.find_one({"id": int(guild_id)})
        return JsonResponse(fix_id(updated))

    def delete(self, request, guild_id):
        result = guild_collection.delete_one({"id": int(guild_id)})

        if result.deleted_count == 0:
            return JsonResponse({"error": "Guild not found"}, status=404)

        return JsonResponse({"status": "Guild deleted"})
