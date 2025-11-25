from django.urls import path, include
from rest_framework import routers
from .views.auth_view import TokenLoginView

# Import your ViewSets
from .views.user_view import UserViewSet
from .views.character_view import CharacterViewSet
from .views.guild_view import GuildViewSet
from .views.item_view import ItemViewSet
from .views.inventory_view import InventoryViewSet
from .views.npc_view import NPCViewSet
from .views.quest_view import QuestViewSet
from .views.skill_view import SkillViewSet
from .views.battle_view import BattleViewSet
from .views.transaction_view import TransactionViewSet
from .views.quest_actions import QuestActionViewSet

router = routers.DefaultRouter()

# Register endpoints
router.register(r'users', UserViewSet, basename='user')
router.register(r'characters', CharacterViewSet, basename='character')
router.register(r'guilds', GuildViewSet, basename='guild')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'inventories', InventoryViewSet, basename='inventory')
router.register(r'npcs', NPCViewSet, basename='npc')
router.register(r'quests', QuestViewSet, basename='quest')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'battles', BattleViewSet, basename='battle')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r"quests", QuestActionViewSet, basename="quest-actions")

urlpatterns = [
    path('', include(router.urls)),

    path("auth/login/", TokenLoginView.as_view()),

]
