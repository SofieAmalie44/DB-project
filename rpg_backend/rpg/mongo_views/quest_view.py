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
quests_collection = db["quest"]


def fix_id(doc):
    """Convert MongoDB _id → string for JSON output"""
    doc["_id"] = str(doc["_id"])
    return doc


@method_decorator(csrf_exempt, name="dispatch")
class MongoQuestList(View):
    """GET all quests / POST create new quest"""

    def get(self, request):
        quests = [fix_id(q) for q in quests_collection.find()]
        return JsonResponse(quests, safe=False)

    def post(self, request):
        body = json.loads(request.body)

        result = quests_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return JsonResponse(body, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class MongoQuestDetail(View):
    """GET one quest / PUT update / DELETE"""

    def get(self, request, quest_id):
        doc = quests_collection.find_one({"id": int(quest_id)})

        if not doc:
            return JsonResponse({"error": "Quest not found"}, status=404)

        return JsonResponse(fix_id(doc))

    def put(self, request, quest_id):
        body = json.loads(request.body)

        result = quests_collection.update_one(
            {"id": int(quest_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return JsonResponse({"error": "Quest not found"}, status=404)

        updated = quests_collection.find_one({"id": int(quest_id)})
        return JsonResponse(fix_id(updated))

    def delete(self, request, quest_id):
        result = quests_collection.delete_one({"id": int(quest_id)})

        if result.deleted_count == 0:
            return JsonResponse({"error": "Quest not found"}, status=404)

        return JsonResponse({"status": "Quest deleted"})
