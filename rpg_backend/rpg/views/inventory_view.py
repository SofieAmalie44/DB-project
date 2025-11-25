from rest_framework import viewsets
from ..models.inventory import Inventory
from ..serializers.inventory_serializer import InventorySerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer