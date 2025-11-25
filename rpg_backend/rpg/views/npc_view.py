from rest_framework import viewsets
from ..models.npc import NPC
from ..serializers.npc_serializer import NPCSerializer


class NPCViewSet(viewsets.ModelViewSet):
    queryset = NPC.objects.all()
    serializer_class = NPCSerializer