from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pymongo import MongoClient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rpg_backend.rpg.mongo_schemas import ItemSchema, ItemListSchema

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
items_collection = db["item"]

def fix_id(doc):
    """Convert ObjectId to string"""
    doc["_id"] = str(doc["_id"])
    return doc

ITEM_NOT_FOUND = {"error": "Item not found"}
HTTP_404 = status.HTTP_404_NOT_FOUND

@method_decorator(csrf_exempt, name='dispatch')
class MongoItemList(APIView):
    """GET all items + CREATE new item"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get all items",
        responses={200: openapi.Response("List of items", schema=ItemListSchema)}
    )
    def get(self, request):
        items = [fix_id(doc) for doc in items_collection.find()]
        return Response(items, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new item",
        request_body=ItemSchema,
        responses={201: openapi.Response("Created item", schema=ItemSchema)}
    )
    def post(self, request):
        body = request.data.copy()

        last = items_collection.find_one(sort=[("id", -1)])
        body["id"] = (last["id"] + 1) if last else 1

        # Insert into MongoDB
        result = items_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return Response(body, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class MongoItemDetail(APIView):
    """GET one item + UPDATE + DELETE"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get item by ID",
        responses={200: openapi.Response("Item", schema=ItemSchema), 404: "Not found"}
    )
    def get(self, request, item_id):
        doc = items_collection.find_one({"id": int(item_id)})
        if not doc:
            return Response(ITEM_NOT_FOUND, status=HTTP_404)
        return Response(fix_id(doc), status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update item by ID",
        request_body=ItemSchema,
        responses={200: openapi.Response("Updated item", schema=ItemSchema), 404: "Not found"}
    )
    def put(self, request, item_id):
        body = request.data.copy()

        if "_id" in body:
            body.pop("_id")
        
        result = items_collection.update_one(
            {"id": int(item_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return Response(ITEM_NOT_FOUND, status=HTTP_404)

        updated = items_collection.find_one({"id": int(item_id)})
        return Response(fix_id(updated), status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete item by ID",
        responses={204: "Item deleted", 404: "Not found"}
    )
    def delete(self, request, item_id):
        result = items_collection.delete_one({"id": int(item_id)})

        if result.deleted_count == 0:
            return Response(ITEM_NOT_FOUND, status=HTTP_404)

        return Response(status=status.HTTP_204_NO_CONTENT)
