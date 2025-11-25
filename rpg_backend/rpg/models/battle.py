from django.db import models
from .character import Character


# =============================
# BATTLE
# =============================
class Battle(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)  
    xp = models.IntegerField(default=0)
    money = models.IntegerField(default=0)
    outcome = models.CharField(max_length=20, choices=[('Victory', 'Victory'), ('Defeat', 'Defeat')])

