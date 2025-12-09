from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pymongo import MongoClient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rpg_backend.rpg.mongo_schemas import NPCSchema, NPCListSchema

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
npc_collection = db["npc"]


def fix_id(doc):
    """Convert ObjectId to string"""
    doc["_id"] = str(doc["_id"])
    return doc

NPC_NOT_FOUND = {"error": "NPC not found"}
HTTP_404 = status.HTTP_404_NOT_FOUND

@method_decorator(csrf_exempt, name="dispatch")
class MongoNPCList(APIView):
    """GET all NPCs / POST create new NPC"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get all NPCs", responses={200: NPCListSchema})
    def get(self, request):
        npcs = [fix_id(doc) for doc in npc_collection.find()]
        return Response(npcs, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Create NPC", request_body=NPCSchema, responses={201: NPCSchema})
    def post(self, request):
        body = request.data.copy()

        last = npc_collection.find_one(sort=[("id", -1)])
        body["id"] = (last["id"] + 1) if last else 1

        result = npc_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return Response(body, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class MongoNPCDetail(APIView):
    """GET one NPC / PUT update / DELETE"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get NPC", responses={200: NPCSchema, 404: "Not found"})
    def get(self, request, npc_id):
        doc = npc_collection.find_one({"id": int(npc_id)})

        if not doc:
            return Response(NPC_NOT_FOUND, status=HTTP_404)

        return Response(fix_id(doc), status=status.HTTP_200_OK)
    
    @swagger_auto_schema(operation_description="Update NPC", request_body=NPCSchema, responses={200: NPCSchema, 404: "Not found"})
    def put(self, request, npc_id):
        body = request.data.copy()

        result = npc_collection.update_one(
            {"id": int(npc_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return Response(NPC_NOT_FOUND, status=HTTP_404)

        updated = npc_collection.find_one({"id": int(npc_id)})
        return Response(fix_id(updated), status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Delete NPC", responses={204: "Deleted", 404: "Not found"})
    def delete(self, request, npc_id):
        result = npc_collection.delete_one({"id": int(npc_id)})

        if result.deleted_count == 0:
            return Response(NPC_NOT_FOUND, status=HTTP_404)

        return Response(status=status.HTTP_204_NO_CONTENT)
