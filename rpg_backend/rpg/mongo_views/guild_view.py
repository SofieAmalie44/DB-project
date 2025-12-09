from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pymongo import MongoClient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


from rpg_backend.rpg.mongo_schemas import GuildSchema, GuildListSchema

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
guild_collection = db["guild"]


def fix_id(doc):
    """Convert ObjectId to string"""
    doc["_id"] = str(doc["_id"])
    return doc

GUILD_NOT_FOUND = {"error": "Guild not found"}
HTTP_404 = status.HTTP_404_NOT_FOUND

@method_decorator(csrf_exempt, name="dispatch")
class MongoGuildList(APIView):
    """GET all guilds / POST create a new guild"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get all guilds", responses={200: GuildListSchema})
    def get(self, request):
        guilds = [fix_id(doc) for doc in guild_collection.find()]
        return Response(guilds, status=status.HTTP_200_OK)

    """
    POST /api/mongodb/guilds/
    {
        "guild_name": "Knights of Dawn",
        "members": 15
    }
    """
    @swagger_auto_schema(operation_description="Create guild", request_body=GuildSchema, responses={201: GuildSchema})
    def post(self, request):
        body = request.data.copy()

        last = guild_collection.find_one(sort=[("id", -1)])
        body["id"] = (last["id"] + 1) if last else 1

        result = guild_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return Response(body, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class MongoGuildDetail(APIView):
    """GET one guild / PUT update / DELETE"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get guild", responses={200: GuildSchema, 404: "Not found"})
    def get(self, request, guild_id):
        doc = guild_collection.find_one({"id": int(guild_id)})
        if not doc:
            return Response(GUILD_NOT_FOUND, status=HTTP_404)
        return Response(fix_id(doc), status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Update guild", request_body=GuildSchema, responses={200: GuildSchema, 404: "Not found"})
    def put(self, request, guild_id):
        body = request.data.copy()

        result = guild_collection.update_one(
            {"id": int(guild_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return Response(GUILD_NOT_FOUND, status=HTTP_404)

        updated = guild_collection.find_one({"id": int(guild_id)})
        return Response(fix_id(updated), status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Delete guild", responses={204: "Deleted", 404: "Not found"})
    def delete(self, request, guild_id):
        result = guild_collection.delete_one({"id": int(guild_id)})

        if result.deleted_count == 0:
            return Response(GUILD_NOT_FOUND, status=HTTP_404)

        return Response({"status": "Guild deleted"}, status=status.HTTP_200_OK)
