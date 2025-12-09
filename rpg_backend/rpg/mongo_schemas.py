from drf_yasg import openapi

# Basic scalar types
Integer = openapi.TYPE_INTEGER
String = openapi.TYPE_STRING
Boolean = openapi.TYPE_BOOLEAN

# ---- Schemas for individual models ----

ItemSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=Integer),
        "name": openapi.Schema(type=String),
        "type": openapi.Schema(type=String),
        "rarity": openapi.Schema(type=String),
        "value": openapi.Schema(type=Integer),
        "stats": openapi.Schema(type=String),
        "_id": openapi.Schema(type=String),
    }
)

SkillSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=Integer),
        "name": openapi.Schema(type=String),
        "description": openapi.Schema(type=String),
        "damage": openapi.Schema(type=Integer),
        "healing": openapi.Schema(type=Integer),
        "_id": openapi.Schema(type=String),
    }
)

NPCSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=Integer),
        "name": openapi.Schema(type=String),
        "role": openapi.Schema(type=String),
        "location": openapi.Schema(type=String),
        "_id": openapi.Schema(type=String),
    }
)

QuestSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=Integer),
        "title": openapi.Schema(type=String),
        "reward_money": openapi.Schema(type=Integer),
        "reward_xp": openapi.Schema(type=Integer),
        "description": openapi.Schema(type=String),
        "npc": openapi.Schema(type=Integer),
        "status": openapi.Schema(type=String),
        "completed_at": openapi.Schema(type=String, format="date-time", nullable=True),
        "_id": openapi.Schema(type=String),
    }
)

GuildSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=Integer),
        "guild_name": openapi.Schema(type=String),
        "members": openapi.Schema(type=Integer),
        "_id": openapi.Schema(type=String),
    }
)

BattleSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=Integer),
        "character": openapi.Schema(type=Integer),
        "xp": openapi.Schema(type=Integer),
        "money": openapi.Schema(type=Integer),
        "outcome": openapi.Schema(type=String),
        "_id": openapi.Schema(type=String),
    }
)

TransactionSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=Integer),
        "user": openapi.Schema(type=Integer),
        "item": openapi.Schema(type=Integer),
        "quantity": openapi.Schema(type=Integer),
        "cost": openapi.Schema(type=Integer),
        "_id": openapi.Schema(type=String),
    }
)

InventoryItemSubschema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "item": openapi.Schema(type=Integer),
        "quantity": openapi.Schema(type=Integer),
    }
)

InventorySchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=Integer),
        "character": openapi.Schema(type=Integer),
        "items": openapi.Schema(type=openapi.TYPE_ARRAY, items=InventoryItemSubschema),
        "_id": openapi.Schema(type=String),
    }
)

UserSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=Integer),
        "username": openapi.Schema(type=String),
        "email": openapi.Schema(type=String),
        "first_name": openapi.Schema(type=String),
        "last_name": openapi.Schema(type=String),
        "is_staff": openapi.Schema(type=Boolean),
        "is_superuser": openapi.Schema(type=Boolean),
        "date_joined": openapi.Schema(type=String, format="date-time"),
        "last_login": openapi.Schema(type=String, format="date-time", nullable=True),
        "_id": openapi.Schema(type=String),
    }
)

# ---- Collection / list wrappers ----
ItemListSchema = openapi.Schema(type=openapi.TYPE_ARRAY, items=ItemSchema)
SkillListSchema = openapi.Schema(type=openapi.TYPE_ARRAY, items=SkillSchema)
NPCListSchema = openapi.Schema(type=openapi.TYPE_ARRAY, items=NPCSchema)
QuestListSchema = openapi.Schema(type=openapi.TYPE_ARRAY, items=QuestSchema)
GuildListSchema = openapi.Schema(type=openapi.TYPE_ARRAY, items=GuildSchema)
BattleListSchema = openapi.Schema(type=openapi.TYPE_ARRAY, items=BattleSchema)
TransactionListSchema = openapi.Schema(type=openapi.TYPE_ARRAY, items=TransactionSchema)
InventoryListSchema = openapi.Schema(type=openapi.TYPE_ARRAY, items=InventorySchema)
UserListSchema = openapi.Schema(type=openapi.TYPE_ARRAY, items=UserSchema)

# ---- Reusable param definitions ----
Param_id = openapi.Parameter("id", openapi.IN_PATH, type=openapi.TYPE_INTEGER)
Param_item_id = openapi.Parameter("item_id", openapi.IN_PATH, type=openapi.TYPE_INTEGER)
Param_inv_id = openapi.Parameter("inv_id", openapi.IN_PATH, type=openapi.TYPE_INTEGER)
