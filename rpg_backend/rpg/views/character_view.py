from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Character
from ..serializers.character_serializer import CharacterSerializer
from ..permissions import IsOwner

class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Character.objects.filter(user=self.request.user)
