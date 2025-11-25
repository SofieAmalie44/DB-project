from rest_framework import serializers
from ..models import Character
from .user_serializer import UserSerializer
from .skill_serializer import SkillSerializer
from .quest_serializer import QuestSerializer
from .battle_serializer import BattleSerializer


# =============================
# CHARACTER
# =============================
class CharacterSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    quests = QuestSerializer(many=True, read_only=True)
    battles = BattleSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = "__all__"