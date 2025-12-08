from django.http import JsonResponse
from django.views import View
from bson import ObjectId
from pymongo import MongoClient
import json

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
battle_collection = db["battle"]


def fix_id(doc):
    """Convert _id ObjectId → string for JSON output."""
    doc["_id"] = str(doc["_id"])
    return doc


@method_decorator(csrf_exempt, name="dispatch")
class MongoBattleList(View):
    """GET all battles / POST create battle"""

    def get(self, request):
        battles = [fix_id(doc) for doc in battle_collection.find()]
        return JsonResponse(battles, safe=False)

    def post(self, request):
        body = json.loads(request.body)

        result = battle_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return JsonResponse(body, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class MongoBattleDetail(View):
    """GET single battle / PUT update / DELETE"""

    def get(self, request, battle_id):
        doc = battle_collection.find_one({"id": int(battle_id)})

        if not doc:
            return JsonResponse({"error": "Battle not found"}, status=404)

        return JsonResponse(fix_id(doc))

    def put(self, request, battle_id):
        body = json.loads(request.body)

        result = battle_collection.update_one(
            {"id": int(battle_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return JsonResponse({"error": "Battle not found"}, status=404)

        updated_doc = battle_collection.find_one({"id": int(battle_id)})
        return JsonResponse(fix_id(updated_doc))

    def delete(self, request, battle_id):
        result = battle_collection.delete_one({"id": int(battle_id)})

        if result.deleted_count == 0:
            return JsonResponse({"error": "Battle not found"}, status=404)

        return JsonResponse({"status": "Battle deleted"})
