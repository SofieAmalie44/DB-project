from rest_framework import serializers
from ..models import Transaction
from .user_serializer import UserSerializer


# =============================
# TRANSACTION
# =============================
class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"