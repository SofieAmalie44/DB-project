from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pymongo import MongoClient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


from rpg_backend.rpg.mongo_schemas import QuestSchema, QuestListSchema

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
quests_collection = db["quest"]


def fix_id(doc):
    """Convert MongoDB _id to string for JSON output"""
    doc["_id"] = str(doc["_id"])
    return doc

QUEST_NOT_FOUND = {"error": "Quest not found"}
HTTP_404 = status.HTTP_404_NOT_FOUND

@method_decorator(csrf_exempt, name="dispatch")
class MongoQuestList(APIView):
    """GET all quests / POST create new quest"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get all quests", responses={200: QuestListSchema})
    def get(self, request):
        quests = [fix_id(q) for q in quests_collection.find()]
        return Response(quests, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Create quest", request_body=QuestSchema, responses={201: QuestSchema})
    def post(self, request):
        body = request.data.copy()

        last = quests_collection.find_one(sort=[("id", -1)])
        body["id"] = (last["id"] + 1) if last else 1

        result = quests_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return Response(body, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class MongoQuestDetail(APIView):
    """GET one quest / PUT update / DELETE"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get quest", responses={200: QuestSchema, 404: "Not found"})
    def get(self, request, quest_id):
        doc = quests_collection.find_one({"id": int(quest_id)})

        if not doc:
            return Response(QUEST_NOT_FOUND, status=HTTP_404)

        return Response(fix_id(doc), status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Update quest", request_body=QuestSchema, responses={200: QuestSchema, 404: "Not found"})
    def put(self, request, quest_id):
        body = request.data.copy()

        result = quests_collection.update_one(
            {"id": int(quest_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return Response(QUEST_NOT_FOUND, status=HTTP_404)

        updated = quests_collection.find_one({"id": int(quest_id)})
        return Response(fix_id(updated), status=status.HTTP_200_OK)
    
    @swagger_auto_schema(operation_description="Delete quest", responses={204: "Deleted", 404: "Not found"})
    def delete(self, request, quest_id):
        result = quests_collection.delete_one({"id": int(quest_id)})

        if result.deleted_count == 0:
            return Response(QUEST_NOT_FOUND, status=HTTP_404)

        return Response(status=status.HTTP_204_NO_CONTENT)
