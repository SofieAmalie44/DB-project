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
transaction_collection = db["transaction"]


def fix_id(doc):
    """Convert ObjectId → string"""
    doc["_id"] = str(doc["_id"])
    return doc


@method_decorator(csrf_exempt, name="dispatch")
class MongoTransactionList(View):
    """GET all transactions / POST create new transaction"""

    def get(self, request):
        transactions = [fix_id(doc) for doc in transaction_collection.find()]
        return JsonResponse(transactions, safe=False)

    def post(self, request):
        body = json.loads(request.body)

        result = transaction_collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return JsonResponse(body, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class MongoTransactionDetail(View):
    """GET one transaction / PUT update / DELETE"""

    def get(self, request, transaction_id):
        doc = transaction_collection.find_one({"id": int(transaction_id)})

        if not doc:
            return JsonResponse({"error": "Transaction not found"}, status=404)

        return JsonResponse(fix_id(doc))

    def put(self, request, transaction_id):
        body = json.loads(request.body)

        result = transaction_collection.update_one(
            {"id": int(transaction_id)},
            {"$set": body}
        )

        if result.matched_count == 0:
            return JsonResponse({"error": "Transaction not found"}, status=404)

        updated = transaction_collection.find_one({"id": int(transaction_id)})
        return JsonResponse(fix_id(updated))

    def delete(self, request, transaction_id):
        result = transaction_collection.delete_one({"id": int(transaction_id)})

        if result.deleted_count == 0:
            return JsonResponse({"error": "Transaction not found"}, status=404)

        return JsonResponse({"status": "Transaction deleted"})
