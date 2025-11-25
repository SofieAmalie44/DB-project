from rest_framework import serializers
from ..models import Inventory


# =============================
# INVENTORY
# =============================
class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"