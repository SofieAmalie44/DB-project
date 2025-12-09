from django.urls import path, include
from rest_framework import routers
from .views.auth_view import TokenLoginView

# Import SQL ViewSets
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

# Import MongoDB ViewSets
from .mongo_views.character_view import MongoCharacterList, MongoCharacterDetail, MongoCharacterFilter
from .mongo_views.item_view import MongoItemList, MongoItemDetail
from .mongo_views.skills_view import MongoSkillList, MongoSkillDetail
from .mongo_views.quest_view import MongoQuestList, MongoQuestDetail
from .mongo_views.npc_view import MongoNPCList, MongoNPCDetail
from .mongo_views.guild_view import MongoGuildList, MongoGuildDetail
from .mongo_views.inventory_view import MongoInventoryList, MongoInventoryDetail, MongoInventoryAddItem, MongoInventoryUpdateItem, MongoInventoryRemoveItem, MongoFilterInventory
from .mongo_views.transaction_view import MongoTransactionList, MongoTransactionDetail
from .mongo_views.battle_view import MongoBattleList, MongoBattleDetail
from .mongo_views.user_view import MongoUserList, MongoUserDetail, MongoUserFilter



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

urlpatterns = [
    path('', include(router.urls)),

    path("auth/login/", TokenLoginView.as_view()),

    # MongoDB CRUD endpoints
    path("mongodb/characters/", MongoCharacterList.as_view(), name="mongo-character-list"),
    path("mongodb/characters/<int:char_id>/", MongoCharacterDetail.as_view(), name="mongo-character-details"),
    path("mongodb/characters/filter/", MongoCharacterFilter.as_view(), name="mongo-character-filter"),

    path("mongodb/items/", MongoItemList.as_view(), name="mongo-item-list"),
    path("mongodb/items/<int:item_id>/", MongoItemDetail.as_view(), name="mongo-item-detail"),

    path("mongodb/skills/", MongoSkillList.as_view(), name="mongo-skill-list"),
    path("mongodb/skills/<int:skill_id>/", MongoSkillDetail.as_view(), name="mongo-skill-detail"),
    
    path("mongodb/quests/", MongoQuestList.as_view(), name="mongo-quest-list"),
    path("mongodb/quests/<int:quest_id>/", MongoQuestDetail.as_view(), name="mongo-quest-detail"),
    
    path("mongodb/npcs/", MongoNPCList.as_view(), name="mongo-npc-list"),
    path("mongodb/npcs/<int:npc_id>/", MongoNPCDetail.as_view(), name="mongo-npc-detail"),
    
    path("mongodb/guilds/", MongoGuildList.as_view(), name="mongo-guild-list"),
    path("mongodb/guilds/<int:guild_id>/", MongoGuildDetail.as_view(), name="mongo-guild-detail"),
    
    path("mongodb/inventory/", MongoInventoryList.as_view(), name="mongo-inventory-list"),
    path("mongodb/inventory/<int:inv_id>/", MongoInventoryDetail.as_view(), name="mongo-inventory-detail"),
    # embedded item management
    path("mongodb/inventory/", MongoInventoryList.as_view()),
    path("mongodb/inventory/<int:inv_id>/", MongoInventoryDetail.as_view()),
    path("mongodb/inventory/<int:inv_id>/add-item/", MongoInventoryAddItem.as_view()),
    path("mongodb/inventory/<int:inv_id>/update-item/<int:item_id>/", MongoInventoryUpdateItem.as_view()),
    path("mongodb/inventory/<int:inv_id>/remove-item/<int:item_id>/", MongoInventoryRemoveItem.as_view()),
    path("mongodb/inventory/filter/", MongoFilterInventory.as_view()),

    path("mongodb/transactions/", MongoTransactionList.as_view(), name="mongo-transaction-list"),
    path("mongodb/transactions/<int:transaction_id>/", MongoTransactionDetail.as_view(), name="mongo-transaction-detail"),
    
    path("mongodb/battles/", MongoBattleList.as_view(), name="mongo-battle-list"),
    path("mongodb/battles/<int:battle_id>/", MongoBattleDetail.as_view(), name="mongo-battle-detail"),

    path("mongodb/users/", MongoUserList.as_view(), name="mongo-user-list"),
    path("mongodb/users/<int:user_id>/", MongoUserDetail.as_view(), name="mongo-user-detail"),
    path("mongodb/users/filter/", MongoUserFilter.as_view(), name="mongo-user-filter"),

]
