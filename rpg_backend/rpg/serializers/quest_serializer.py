from rest_framework import serializers
from ..models import Quest
from ..models.npc import NPC

# =============================
# QUEST
# =============================
class QuestSerializer(serializers.ModelSerializer):
    npc_name = serializers.CharField(source="npc.name", read_only=True)

    class Meta:
        model = Quest
        fields = [
            "id",
            "title",
            "description",
            "reward_money",
            "reward_xp",
            "npc_id",
            "npc_name"
        ]



