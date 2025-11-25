from rest_framework import viewsets
from ..models.guild import Guild
from ..serializers.guild_serializer import GuildSerializer

class GuildViewSet(viewsets.ModelViewSet):
    queryset = Guild.objects.all()
    serializer_class = GuildSerializer