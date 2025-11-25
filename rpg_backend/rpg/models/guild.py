from django.db import models


# =============================
# GUILD
# =============================
class Guild(models.Model):
    guild_name = models.CharField(max_length=100, unique=True)
    members = models.IntegerField(default=0)

    def __str__(self):
        return self.guild_name