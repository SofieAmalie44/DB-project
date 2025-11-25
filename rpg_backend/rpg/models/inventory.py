from django.db import models
# from .item import Item
# from .character import Character

# =============================
# INVENTORY
# =============================
class Inventory(models.Model):
    character = models.ForeignKey(
        "rpg.Character",
        on_delete=models.CASCADE,
        related_name="inventories"
    )
    item = models.ForeignKey(
        "rpg.Item",
        on_delete=models.CASCADE,
        related_name="inventories"
    )
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.character.name} owns {self.quantity} × {self.item.name}"


