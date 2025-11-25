from django.db import models


# =============================
# ITEM
# =============================
class Item(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, blank=True, null=True)
    rarity = models.CharField(max_length=50)
    value = models.IntegerField(null=True, blank=True)
    stats = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name