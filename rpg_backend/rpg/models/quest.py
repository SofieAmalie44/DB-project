from django.db import models
from .npc import NPC

# =============================
# GUEST
# =============================
class Quest(models.Model):
    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    title = models.CharField(max_length=100)
    reward_money = models.IntegerField(null=True, blank=True)
    reward_xp = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    npc = models.ForeignKey(NPC, on_delete=models.CASCADE)

    # NEW FIELDS
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="not_started"
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
