from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pymongo import MongoClient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
characters_collection = db["character"]


def fix_id(doc):
    """Convert _id ObjectId to string"""
    doc["_id"] = str(doc["_id"])
    return doc

CHAR_NOT_FOUND = {"error": "Character not found"}
HTTP_404 = status.HTTP_404_NOT_FOUND

@method_decorator(csrf_exempt, name='dispatch')
class MongoCharacterList(APIView):

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve all characters stored in MongoDB",
        responses={200: "List of characters"}
    )

    def get(self, request):
        """Get all characters from MongoDB"""
        data = [fix_id(doc) for doc in characters_collection.find()]
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new character",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "character_name": openapi.Schema(type=openapi.TYPE_STRING),
                "user": openapi.Schema(type=openapi.TYPE_INTEGER),
                "level": openapi.Schema(type=openapi.TYPE_INTEGER),
                "hp": openapi.Schema(type=openapi.TYPE_INTEGER),
                "mana": openapi.Schema(type=openapi.TYPE_INTEGER),
                "xp": openapi.Schema(type=openapi.TYPE_INTEGER),
                "gold": openapi.Schema(type=openapi.TYPE_INTEGER),
                "guild": openapi.Schema(type=openapi.TYPE_INTEGER),
                "skills": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
                "quests": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
            }
        ),
        responses={201: "Character created"}
    )

    def post(self, request):
        """Create a new character in MongoDB"""
        body = request.data.copy()

        last = characters_collection.find_one(sort=[("id", -1)])
        body["id"] = (last["id"] + 1) if last else 1
        # forces defult lists
        body.setdefault("skills", [])
        body.setdefault("quests", [])

        result = characters_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)
        return Response(body, status=status.HTTP_201_CREATED)
    

@method_decorator(csrf_exempt, name='dispatch')
class MongoCharacterDetail(APIView):

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get a character by ID",
        responses={200: "Character data returned successfully", 404: "Character not found"}
    )

    def get(self, request, char_id):
        """Get a single character"""
        doc = characters_collection.find_one({"id": int(char_id)})

        if not doc:
            return Response(CHAR_NOT_FOUND, status=HTTP_404)

        return Response(fix_id(doc), status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a character by ID.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "character_name": openapi.Schema(type=openapi.TYPE_STRING),
                "level": openapi.Schema(type=openapi.TYPE_INTEGER),
                "hp": openapi.Schema(type=openapi.TYPE_INTEGER),
                "mana": openapi.Schema(type=openapi.TYPE_INTEGER),
                "xp": openapi.Schema(type=openapi.TYPE_INTEGER),
                "gold": openapi.Schema(type=openapi.TYPE_INTEGER),
                "guild": openapi.Schema(type=openapi.TYPE_INTEGER),
                "skills": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
                "quests": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
            }
        ),
        responses={200: "Character updated.", 404: "Character not found."}
    )
    def put(self, request, char_id):
        """Update a character"""
        body = request.data.copy()

        result = characters_collection.update_one(
            {"id": int(char_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return Response(CHAR_NOT_FOUND, status=HTTP_404)

        updated = characters_collection.find_one({"id": int(char_id)})
        return Response(fix_id(updated), status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_description="Delete a character by ID.",
        responses={200: "Character deleted.", 404: "Character not found."}
    )
    def delete(self, request, char_id):
        """Delete a character"""
        result = characters_collection.delete_one({"id": int(char_id)})

        if result.deleted_count == 0:
            return Response(CHAR_NOT_FOUND, status=HTTP_404)

        return Response({"status": "Character deleted"}, status=status.HTTP_200_OK)
    

@method_decorator(csrf_exempt, name='dispatch')
class MongoCharacterFilter(APIView):

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Filter characters by name, minimum level, or guild.",
        manual_parameters=[
            openapi.Parameter(
                "name", openapi.IN_QUERY, description="Partial name match", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "min_level", openapi.IN_QUERY, description="Minimum level", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "guild", openapi.IN_QUERY, description="Guild ID", type=openapi.TYPE_INTEGER
            ),
        ],
        responses={200: "Filtered character list"}
    )

    def get(self, request):
        query = {}

        name = request.GET.get("name")
        min_level = request.GET.get("min_level")
        guild = request.GET.get("guild")

        if name:
            query["character_name"] = {"$regex": name, "$options": "i"}

        if min_level:
            query["level"] = {"$gte": int(min_level)}

        if guild:
            query["guild"] = int(guild)

        characters = [fix_id(c) for c in characters_collection.find(query)]
        return Response(characters, status=status.HTTP_200_OK)