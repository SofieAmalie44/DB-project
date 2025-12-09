from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pymongo import MongoClient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rpg_backend.rpg.mongo_schemas import BattleSchema, BattleListSchema

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
battle_collection = db["battle"]


def fix_id(doc):
    """Convert _id ObjectId to string"""
    doc["_id"] = str(doc["_id"])
    return doc

BATTLE_NOT_FOUND = {"error": "Battle not found"}
HTTP_404 = status.HTTP_404_NOT_FOUND

@method_decorator(csrf_exempt, name="dispatch")
class MongoBattleList(APIView):

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]
    """GET all battles / POST create battle"""

    @swagger_auto_schema(operation_description="Get all battles", responses={200: BattleListSchema})
    def get(self, request):
        battles = [fix_id(doc) for doc in battle_collection.find()]
        return Response(battles, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Create battle", request_body=BattleSchema, responses={201: BattleSchema})
    def post(self, request):
        body = request.data.copy()

        last = battle_collection.find_one(sort=[("id", -1)])
        body["id"] = (last["id"] + 1) if last else 1

        body.setdefault("xp", 0)
        body.setdefault("money", 0)

        result = battle_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return Response(body, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class MongoBattleDetail(APIView):
    """GET single battle / PUT update / DELETE"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get battle", responses={200: BattleSchema, 404: "Not found"})
    def get(self, request, battle_id):
        doc = battle_collection.find_one({"id": int(battle_id)})

        if not doc:
            return Response(BATTLE_NOT_FOUND, status=HTTP_404)

        return Response(fix_id(doc), status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Update battle", request_body=BattleSchema, responses={200: BattleSchema, 404: "Not found"})
    def put(self, request, battle_id):
        body = request.data.copy()

        result = battle_collection.update_one(
            {"id": int(battle_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return Response(BATTLE_NOT_FOUND, status=HTTP_404)

        updated_doc = battle_collection.find_one({"id": int(battle_id)})
        return Response(fix_id(updated_doc), status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Delete battle", responses={204: "Deleted", 404: "Not found"})
    def delete(self, request, battle_id):
        result = battle_collection.delete_one({"id": int(battle_id)})

        if result.deleted_count == 0:
            return Response(BATTLE_NOT_FOUND, status=HTTP_404)

        return Response(status=status.HTTP_204_NO_CONTENT)
