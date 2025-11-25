from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from rpg_backend.rpg.models.quest import Quest
from rpg_backend.rpg.models.character import Character
from rpg_backend.rpg.models.skill import Skill
from rpg_backend.rpg.models.inventory import Inventory
from rpg_backend.rpg.serializers.quest_serializer import QuestSerializer

from django.db import connection

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class QuestActionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # -----------------------------
    # START QUEST
    # -----------------------------
    @action(detail=True, methods=["post"])

    @swagger_auto_schema(
    operation_summary="Start a quest",
    operation_description="Adds the quest to the player's active quests.",
    tags=["Quests"],
    responses={200: "Quest started", 404: "Quest not found"}
    )
    @action(detail=True, methods=["post"])

    def start(self, request, pk=None):
        user = request.user
        quest_id = pk

        # Check quest exists
        try:
            quest = Quest.objects.get(pk=quest_id)
        except Quest.DoesNotExist:
            return Response({"error": "Quest not found"}, status=404)

        # Get user character
        character = Character.objects.get(user=user)

        # Check if already started
        if character.quests.filter(pk=quest_id).exists():
            return Response({"message": "Quest already started"}, status=200)

        # Add quest to active quests
        character.quests.add(quest)

        return Response(
            {"message": "Quest started", "quest_id": quest_id},
            status=201,
        )

    # -----------------------------
    # COMPLETE QUEST
    # -----------------------------
    @action(detail=True, methods=["post"])

    @swagger_auto_schema(
    operation_summary="Complete a quest",
    operation_description="Grants gold, XP, and handles level-up logic.",
    tags=["Quests"],
    responses={200: "Quest completed", 400: "Quest not active"}
    )
    @action(detail=True, methods=["post"])

    def complete(self, request, pk=None):
        user = request.user
        quest_id = pk

        try:
            quest = Quest.objects.get(pk=quest_id)
        except Quest.DoesNotExist:
            return Response({"error": "Quest not found"}, status=404)

        character = Character.objects.get(user=user)

        # Check if user has started quest
        if not character.quests.filter(pk=quest_id).exists():
            return Response({"error": "Quest not active"}, status=400)

        # Remove from active quests
        character.quests.remove(quest)

        # Apply rewards
        gold_before = character.gold
        xp_before = character.xp

        character.gold += quest.reward_money or 0
        character.xp += quest.reward_xp or 0

        # Level-up logic
        level_up = False
        while character.xp >= 100:
            character.level += 1
            character.xp -= 100
            level_up = True

        character.save()

        return Response(
            {
                "message": "Quest completed",
                "quest_id": quest_id,
                "gold_gained": (quest.reward_money or 0),
                "xp_gained": (quest.reward_xp or 0),
                "level_up": level_up,
            },
            status=200,
        )

    # -----------------------------
    # ABANDON QUEST
    # -----------------------------
    @action(detail=True, methods=["delete"])

    @swagger_auto_schema(
    operation_summary="Abandon a quest",
    operation_description="Removes the quest from the player's active list.",
    tags=["Quests"],
    responses={200: "Quest abandoned", 400: "Quest not active"}
    )
    @action(detail=True, methods=["delete"])

    def abandon(self, request, pk=None):
        user = request.user
        quest_id = pk

        try:
            quest = Quest.objects.get(pk=quest_id)
        except Quest.DoesNotExist:
            return Response({"error": "Quest not found"}, status=404)

        character = Character.objects.get(user=user)

        # Check if user has quest active
        if not character.quests.filter(pk=quest_id).exists():
            return Response({"error": "Quest not active"}, status=400)

        # Remove quest
        character.quests.remove(quest)

        return Response(
            {"message": "Quest abandoned", "quest_id": quest_id},
            status=200,
        )
