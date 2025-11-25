from django.db import models


# =============================
# SKILL
# =============================
class Skill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    damage = models.IntegerField(null=True, blank=True)
    healing = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name