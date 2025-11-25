from rest_framework import serializers
from ..models import Battle


# =============================
# BATTLE
# =============================
class BattleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Battle
        fields = "__all__"