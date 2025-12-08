from django.db import models
from .inventory import Inventory

class InventoryItem(models.Model):
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name="items"
    )
    item = models.ForeignKey(
        "rpg.Item",
        on_delete=models.CASCADE,
        related_name="inventory_items"
    )
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.item.name} x{self.quantity} in {self.inventory}"
