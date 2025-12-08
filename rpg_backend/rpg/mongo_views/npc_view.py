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
npc_collection = db["npc"]


def fix_id(doc):
    """Convert ObjectId to string for JSON output"""
    doc["_id"] = str(doc["_id"])
    return doc


@method_decorator(csrf_exempt, name="dispatch")
class MongoNPCList(View):
    """GET all NPCs / POST create new NPC"""

    def get(self, request):
        npcs = [fix_id(doc) for doc in npc_collection.find()]
        return JsonResponse(npcs, safe=False)

    def post(self, request):
        body = json.loads(request.body)

        result = npc_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return JsonResponse(body, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class MongoNPCDetail(View):
    """GET one NPC / PUT update / DELETE"""

    def get(self, request, npc_id):
        doc = npc_collection.find_one({"id": int(npc_id)})

        if not doc:
            return JsonResponse({"error": "NPC not found"}, status=404)

        return JsonResponse(fix_id(doc))

    def put(self, request, npc_id):
        body = json.loads(request.body)

        result = npc_collection.update_one(
            {"id": int(npc_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return JsonResponse({"error": "NPC not found"}, status=404)

        updated = npc_collection.find_one({"id": int(npc_id)})
        return JsonResponse(fix_id(updated))

    def delete(self, request, npc_id):
        result = npc_collection.delete_one({"id": int(npc_id)})

        if result.deleted_count == 0:
            return JsonResponse({"error": "NPC not found"}, status=404)

        return JsonResponse({"status": "NPC deleted"})
