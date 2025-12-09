from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pymongo import MongoClient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rpg_backend.rpg.mongo_schemas import TransactionSchema, TransactionListSchema

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
transaction_collection = db["transaction"]


def fix_id(doc):
    """Convert ObjectId to string"""
    doc["_id"] = str(doc["_id"])
    return doc

TRANSACTION_NOT_FOUND = {"error": "Transaction not found"}
HTTP_404 = status.HTTP_404_NOT_FOUND

@method_decorator(csrf_exempt, name="dispatch")
class MongoTransactionList(APIView):
    """GET all transactions / POST create new transaction"""
    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get all transactions", responses={200: TransactionListSchema})
    def get(self, request):
        transactions = [fix_id(doc) for doc in transaction_collection.find()]
        return Response(transactions, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Create transaction", request_body=TransactionSchema, responses={201: TransactionSchema})
    def post(self, request):
        body = request.data.copy()

        result = transaction_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return Response(body, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class MongoTransactionDetail(APIView):
    """GET one transaction / PUT update / DELETE"""

    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get transaction", responses={200: TransactionSchema, 404: "Not found"})
    def get(self, request, transaction_id):
        doc = transaction_collection.find_one({"id": int(transaction_id)})

        if not doc:
            return Response(TRANSACTION_NOT_FOUND, status=HTTP_404)

        return Response(fix_id(doc), status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Update transaction", request_body=TransactionSchema, responses={200: TransactionSchema, 404: "Not found"})
    def put(self, request, transaction_id):
        body = request.data.copy()

        result = transaction_collection.update_one(
            {"id": int(transaction_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return Response(TRANSACTION_NOT_FOUND, status=HTTP_404)

        updated = transaction_collection.find_one({"id": int(transaction_id)})
        return Response(fix_id(updated), status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Delete transaction", responses={204: "Deleted", 404: "Not found"})
    def delete(self, request, transaction_id):
        result = transaction_collection.delete_one({"id": int(transaction_id)})

        if result.deleted_count == 0:
            return Response(TRANSACTION_NOT_FOUND, status=HTTP_404)

        return Response(status=status.HTTP_204_NO_CONTENT)
