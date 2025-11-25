from rest_framework import viewsets
from ..models.battle import Battle
from ..serializers.battle_serializer import BattleSerializer

class BattleViewSet(viewsets.ModelViewSet):
    queryset = Battle.objects.all()
    serializer_class = BattleSerializer