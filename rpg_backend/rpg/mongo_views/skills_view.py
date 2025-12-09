from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pymongo import MongoClient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rpg_backend.rpg.mongo_schemas import SkillSchema, SkillListSchema

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
skills_collection = db["skill"]


def fix_id(doc):
    """Convert MongoDB ObjectId to string"""
    doc["_id"] = str(doc["_id"])
    return doc

SKILL_NOT_FOUND = {"error": "Skill not found"}
HTTP_404 = status.HTTP_404_NOT_FOUND

@method_decorator(csrf_exempt, name="dispatch")
class MongoSkillList(APIView):
    """List all skills or create a new skill"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get all skills",
        responses={200: SkillListSchema}
    )
    def get(self, request):
        skills = [fix_id(doc) for doc in skills_collection.find()]
        return Response(skills, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create skill",
        request_body=SkillSchema,
        responses={201: SkillSchema}
    )
    def post(self, request):
        body = request.data.copy()

        last = skills_collection.find_one(sort=[("id", -1)])
        body["id"] = (last["id"] + 1) if last else 1

        result = skills_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return Response(body, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class MongoSkillDetail(APIView):
    """Retrieve, update, or delete a skill"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get a skill by ID",
        responses={200: SkillSchema, 404: "Not found"}
    )
    def get(self, request, skill_id):
        doc = skills_collection.find_one({"id": int(skill_id)})

        if not doc:
            return Response(SKILL_NOT_FOUND, status=HTTP_404)

        return Response(fix_id(doc), status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a skill by ID",
        request_body=SkillSchema,
        responses={200: SkillSchema, 404: "Not found"}
    )
    def put(self, request, skill_id):
        body = request.data.copy()

        result = skills_collection.update_one(
            {"id": int(skill_id)}, {"$set": body}
        )

        if result.matched_count == 0:
            return Response(SKILL_NOT_FOUND, status=HTTP_404)

        updated = skills_collection.find_one({"id": int(skill_id)})
        return Response(fix_id(updated), status=status.HTTP_200_OK)
    
    @swagger_auto_schema(operation_description="Delete a skill", responses={204: "Deleted", 404: "Not found"})
    def delete(self, request, skill_id):
        result = skills_collection.delete_one({"id": int(skill_id)})

        if result.deleted_count == 0:
            return Response(SKILL_NOT_FOUND, status=HTTP_404)

        return Response(status=status.HTTP_204_NO_CONTENT)
