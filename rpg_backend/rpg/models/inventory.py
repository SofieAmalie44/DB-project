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
        related_name="inventory"
    )

    def __str__(self):
        return f"Inventory of {self.character.name}"



