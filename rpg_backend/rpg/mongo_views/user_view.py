from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pymongo import MongoClient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rpg_backend.rpg.mongo_schemas import UserSchema, UserListSchema

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rpg_mongo"]
user_collection = db["user"]


def fix_id(doc):
    """Convert _id ObjectId to string"""
    doc["_id"] = str(doc["_id"])
    return doc

@method_decorator(csrf_exempt, name="dispatch")
class MongoUserList(APIView):
    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get all users (read-only)", responses={200: UserListSchema})
    def get(self, request):
        users = [fix_id(doc) for doc in user_collection.find()]
        return Response(users, status=status.HTTP_200_OK)
    

@method_decorator(csrf_exempt, name='dispatch')
class MongoUserDetail(APIView):
    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_description="Get user by ID", responses={200: UserSchema, 404: "Not found"})
    def get(self, request, user_id):
        """Get a single user"""
        doc = user_collection.find_one({"id": int(user_id)})

        if not doc:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(fix_id(doc), status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class MongoUserFilter(APIView):
    # Endpoints public / no authentication required
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Filter users by username, email or staff flag",
        manual_parameters=[
            openapi.Parameter("username", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("email", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("is_staff", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
        ],
        responses={200: UserListSchema}
    )
    def get(self, request):
        query = {}

        username = request.GET.get("username")
        email = request.GET.get("email")
        is_staff = request.GET.get("is_staff")

        if username:
            query["username"] = {"$regex": username, "$options": "i"}

        if email:
            query["email"] = {"$regex": email, "$options": "i"}

        if is_staff is not None:
            query["is_staff"] = (is_staff.lower() == "true")

        users = [fix_id(doc) for doc in user_collection.find(query)]
        return Response(users, safe=status.HTTP_200_OK)
