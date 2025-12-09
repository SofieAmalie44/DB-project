from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pymongo import MongoClient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rpg_backend.rpg.mongo_schemas import (
    InventorySchema, InventoryListSchema, InventoryItemSubschema
)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
inventory_collection = db["inventory"]


def fix_id(doc):
    """Convert ObjectId to string"""
    doc["_id"] = str(doc["_id"])
    return doc

INVENTORY_NOT_FOUND = {"error": "Inventory not found"}
HTTP_404 = status.HTTP_404_NOT_FOUND

@method_decorator(csrf_exempt, name="dispatch")
class MongoInventoryList(APIView):
    """GET all inventory entries / POST create new inventory entry"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get all inventory entries", responses={200: InventoryListSchema})
    def get(self, request):
        items = [fix_id(doc) for doc in inventory_collection.find()]
        return Response(items, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create inventory entry",
        request_body=InventorySchema,
        responses={201: InventorySchema}
    )
    def post(self, request):
        body = request.data.copy()

        last = inventory_collection.find_one(sort=[("id", -1)])
        body["id"] = (last["id"] + 1) if last else 1

        # default empty item list
        if "items" not in body:
            body["items"] = []

        result = inventory_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return Response(body, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class MongoInventoryDetail(APIView):
    """GET one inventory entry / DELETE"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get inventory entry", responses={200: InventorySchema, 404: "Not found"})
    def get(self, request, inv_id):
        doc = inventory_collection.find_one({"id": int(inv_id)})

        if not doc:
            return Response(INVENTORY_NOT_FOUND, status=HTTP_404)

        return Response(fix_id(doc), status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Delete inventory entry", responses={204: "Deleted", 404: "Not found"})
    def delete(self, request, inv_id):
        result = inventory_collection.delete_one({"id": int(inv_id)})

        if result.deleted_count == 0:
            return Response(INVENTORY_NOT_FOUND, status=HTTP_404)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
# Add item to inventory
add_item_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={"item": openapi.Schema(type=openapi.TYPE_INTEGER), "quantity": openapi.Schema(type=openapi.TYPE_INTEGER)}
)
    
@method_decorator(csrf_exempt, name="dispatch")
class MongoInventoryAddItem(APIView):
    """
    POST /api/mongodb/inventory/<id</add-item/
    {
        "item": 2,
        "quantity": 5
    }
    """

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Add item to inventory",
                         request_body=add_item_schema,
                         responses={201: InventorySchema, 404: "Not found"})
    def post(self, request, inv_id):
        body = request.data.copy()
        item_id = body.get("item")
        quantity = body.get("quantity", 1)

        inventory = inventory_collection.find_one({"id": int(inv_id)})
        if not inventory:
            return Response(INVENTORY_NOT_FOUND, status=HTTP_404)
        
        # checking if item already exists
        for entry in inventory["items"]:
            if entry["item"] == item_id:
                entry["quantity"] += quantity
                break
        else:
            # add new item
            inventory["items"].append({
                "item": item_id,
                "quantity": quantity
            })
        
        inventory_collection.update_one(
            {"id": int(inv_id)},
            {"$set": {"items": inventory["items"]}}
        )

        inventory = inventory_collection.find_one({"id": int(inv_id)})
        return Response(fix_id(inventory), status=status.HTTP_201_CREATED)

# Update specific item quantity
update_item_schema = openapi.Schema(type=openapi.TYPE_OBJECT, properties={"quantity": openapi.Schema(type=openapi.TYPE_INTEGER)})

@method_decorator(csrf_exempt, name="dispatch")
class MongoInventoryUpdateItem(APIView):
    """
    PATCH /api/mongodb/inventory/<id>/update-item/<item_id>/
    {
        "quantity": 10
    }
    """

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Update item quantity in inventory", request_body=update_item_schema, responses={200: InventorySchema, 404: "Not found"})
    def put(self, request, inv_id, item_id):
        body = request.data.copy()
        new_quantity = body.get("quantity")

        inventory = inventory_collection.find_one({"id": int(inv_id)})
        if not inventory:
            return Response(INVENTORY_NOT_FOUND, status=HTTP_404)
        
        updated = False

        for entry in inventory["items"]:
            if entry["item"] == int(item_id):
                entry["quantity"] = new_quantity
                updated = True

        if not updated:
            return Response(INVENTORY_NOT_FOUND, status=HTTP_404)
        
        inventory_collection.update_one(
            {"id": int(inv_id)},
            {"$set": {"items": inventory["items"]}}
        )

        updated = inventory_collection.find_one({"id": int(inv_id)})
        return Response(fix_id(updated), status=status.HTTP_200_OK)
    

@method_decorator(csrf_exempt, name="dispatch")
class MongoInventoryRemoveItem(APIView):
    """
    DELETE /api/mongodb/inventory/<id>/remove-item/<item_id>/
    """

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Remove item from inventory", responses={200: InventorySchema, 404: "Not found"})
    def delete(self, request, inv_id, item_id):
        inventory = inventory_collection.find_one({"id": int(inv_id)})
        if not inventory:
            return Response(INVENTORY_NOT_FOUND, status=HTTP_404)
        
        before = len(inventory["items"])
        inventory["items"] = [
            x for x in inventory["items"]
            if x["item"] != int(item_id)
        ]
        after = len(inventory["items"])

        if before == after:
            return Response(INVENTORY_NOT_FOUND, status=HTTP_404)
        
        inventory_collection.update_one(
            {"id": int(inv_id)},
            {"$set": {"items": inventory["items"]}}
        )

        return Response(fix_id(inventory), status=status.HTTP_200_OK)
    

@method_decorator(csrf_exempt, name="dispatch")
class MongoFilterInventory(APIView):

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Filter inventory by character or item",
        manual_parameters=[
            openapi.Parameter("character", openapi.IN_QUERY, description="Character ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter("item", openapi.IN_QUERY, description="Item ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: InventoryListSchema}
    )
    def get(self, request):
        query ={}

        character = request.GET.get("character")
        item = request.GET.get("item")

        if character:
            query["character"] = int(character)

        if item:
            query["items.item"] = int(item)

        inventories = [fix_id(doc) for doc in inventory_collection.find(query)]
        return Response(inventories, status=status.HTTP_200_OK)