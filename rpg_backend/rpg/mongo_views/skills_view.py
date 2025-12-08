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
skills_collection = db["skill"]


def fix_id(doc):
    """Convert MongoDB ObjectId → string"""
    doc["_id"] = str(doc["_id"])
    return doc


@method_decorator(csrf_exempt, name="dispatch")
class MongoSkillList(View):
    """List all skills OR create a new skill"""

    def get(self, request):
        skills = [fix_id(doc) for doc in skills_collection.find()]
        return JsonResponse(skills, safe=False)

    def post(self, request):
        body = json.loads(request.body)

        result = skills_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return JsonResponse(body, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class MongoSkillDetail(View):
    """Retrieve, update, or delete a skill"""

    def get(self, request, skill_id):
        doc = skills_collection.find_one({"id": int(skill_id)})

        if not doc:
            return JsonResponse({"error": "Skill not found"}, status=404)

        return JsonResponse(fix_id(doc))

    def put(self, request, skill_id):
        body = json.loads(request.body)

        result = skills_collection.update_one(
            {"id": int(skill_id)}, {"$set": body}
        )

        if result.matched_count == 0:
            return JsonResponse({"error": "Skill not found"}, status=404)

        updated = skills_collection.find_one({"id": int(skill_id)})
        return JsonResponse(fix_id(updated))

    def delete(self, request, skill_id):
        result = skills_collection.delete_one({"id": int(skill_id)})

        if result.deleted_count == 0:
            return JsonResponse({"error": "Skill not found"}, status=404)

        return JsonResponse({"status": "Skill deleted"})
