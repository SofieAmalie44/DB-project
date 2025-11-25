from rest_framework import viewsets
from ..models.quest import Quest
from ..serializers.quest_serializer import QuestSerializer

class QuestViewSet(viewsets.ModelViewSet):
    queryset = Quest.objects.all()
    serializer_class = QuestSerializer
