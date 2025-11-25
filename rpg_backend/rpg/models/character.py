from django.db import models
from django.contrib.auth.models import User
from .guild import Guild
from .quest import Quest
from .skill import Skill



# =============================
# CHARACTER
# =============================
class Character(models.Model):
    character_name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    hp = models.IntegerField(default=100)
    mana = models.IntegerField(default=50)
    xp = models.IntegerField(default=0)
    gold = models.IntegerField(default=0)

    guild = models.ForeignKey(Guild, on_delete=models.SET_NULL, null=True)

    skills = models.ManyToManyField(Skill, blank=True)
    quests = models.ManyToManyField(Quest, blank=True)

    def __str__(self):
        return self.character_name
