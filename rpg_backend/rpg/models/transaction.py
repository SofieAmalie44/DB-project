from django.db import models
from django.contrib.auth.models import User
from .item import Item


# =============================
# TRANSACTION
# =============================
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    cost = models.IntegerField(default=0)


