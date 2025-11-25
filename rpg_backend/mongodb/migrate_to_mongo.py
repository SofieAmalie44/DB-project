#!/usr/bin/env python3
"""
migrate_to_mongo.py

Standalone script to migrate selected Django (MySQL) data into MongoDB.

It uses Django's ORM for reads and `pymongo` for writes. It denormalizes
and embeds related entities to make document reads efficient.

Configuration (environment variables):
- `DJANGO_SETTINGS_MODULE` must be set (e.g. `rpg_backend.settings`).
- `MONGO_URI` default: `mongodb://localhost:27017`
- `MONGO_DB` default: `rpg_mongo`

Run: `python migrate_to_mongo.py`
"""

import os
import sys
from pprint import pprint

# Minimal Django setup
PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ.get("DJANGO_SETTINGS_MODULE", "rpg_backend.settings"))

# Allow overriding DB credentials via environment variables so you don't have to
# edit settings.py just to run this migration script. If any SQL_* env var is
# provided the script will patch the settings module's DATABASES before setup.
SQL_NAME = os.environ.get("SQL_NAME")
SQL_USER = os.environ.get("SQL_USER")
SQL_PASSWORD = os.environ.get("SQL_PASSWORD")
SQL_HOST = os.environ.get("SQL_HOST")
SQL_PORT = os.environ.get("SQL_PORT")

if any([SQL_NAME, SQL_USER, SQL_PASSWORD, SQL_HOST, SQL_PORT]):
    # import the settings module and patch DATABASES
    import importlib
    settings_mod_name = os.environ.get("DJANGO_SETTINGS_MODULE", "rpg_backend.settings")
    settings_mod = importlib.import_module(settings_mod_name)

    default_db = settings_mod.DATABASES.get("default", {})
    patched = default_db.copy()
    if SQL_NAME:
        patched["NAME"] = SQL_NAME
    if SQL_USER:
        patched["USER"] = SQL_USER
    if SQL_PASSWORD:
        patched["PASSWORD"] = SQL_PASSWORD
    if SQL_HOST:
        patched["HOST"] = SQL_HOST
    if SQL_PORT:
        patched["PORT"] = SQL_PORT

    settings_mod.DATABASES["default"] = patched

import django
django.setup()

from django.contrib.auth.models import User
from rpg.models.character import Character
from rpg.models.item import Item
from rpg.models.inventory import Inventory
from rpg.models.skill import Skill
from rpg.models.quests import Quest
from rpg.models.npc import NPC
from rpg.models.battle import Battle
from rpg.models.guild import Guild
from rpg.models.transaction import Transaction

from pymongo import MongoClient
from django.db import connections
from django.db.utils import OperationalError
import traceback


def connect_mongo(uri, dbname):
    client = MongoClient(uri)
    return client, client[dbname]


def test_sql_connection():
    """Try to open a connection to the default Django database and raise a
    friendly error if it fails (e.g. access denied / wrong password).
    """
    try:
        conn = connections["default"]
        conn.ensure_connection()
        return True
    except OperationalError as e:
        print("ERROR: cannot connect to the SQL database using Django settings.")
        print("Django database error:")
        print(str(e))
        # Common MySQL access denied code is 28000. Provide actionable hints.
        print("")
        print("Common fixes:")
        print(" - Verify credentials in rpg_backend/settings.py (USER/PASSWORD)")
        print(" - Ensure the DB user exists and has privileges for the host (localhost vs 127.0.0.1)")
        print(" - If MySQL runs locally, test with the mysql client: `mysql -u USER -p -h 127.0.0.1 -P 3306`")
        print(" - Install the Python connector if missing: pip install mysql-connector-python")
        print("")
        # print a short traceback for debugging
        traceback.print_exc()
        return False


def serialize_item(item):
    return {
        "id": item.id,
        "name": item.name,
        "type": item.type,
        "rarity": item.rarity,
        "value": item.value,
        "stats": item.stats,
    }


def serialize_skill(skill):
    return {"id": skill.id, "name": skill.name, "description": skill.description, "damage": skill.damage, "healing": skill.healing}


def serialize_npc(npc):
    return {"id": npc.id, "name": npc.name, "role": npc.role, "location": npc.location}


def serialize_quest(q):
    return {
        "id": q.id,
        "title": q.title,
        "reward_money": q.reward_money,
        "reward_xp": q.reward_xp,
        "description": q.description,
        "npc": serialize_npc(q.npc) if q.npc else None,
    }


def serialize_battle(b):
    return {"id": b.id, "outcome": b.outcome, "xp": b.xp, "money": b.money}


def migrate_collections(db):
    # Replace collections to make run idempotent for a fresh run
    names = ["items", "skills", "npcs", "quests", "battles", "guilds", "users", "characters"]
    for n in names:
        if n in db.list_collection_names():
            db.drop_collection(n)

    # Items
    items_coll = db["items"]
    for item in Item.objects.all():
        items_coll.insert_one(serialize_item(item))

    # Skills
    skills_coll = db["skills"]
    for s in Skill.objects.all():
        skills_coll.insert_one(serialize_skill(s))

    # NPCs
    npcs_coll = db["npcs"]
    for n in NPC.objects.all():
        npcs_coll.insert_one(serialize_npc(n))

    # Quests (embed NPC)
    quests_coll = db["quests"]
    for q in Quest.objects.select_related("npc").all():
        quests_coll.insert_one(serialize_quest(q))

    # Battles
    battles_coll = db["battles"]
    for b in Battle.objects.all():
        battles_coll.insert_one(serialize_battle(b))

    # Guilds: include member character names (denormalized)
    guilds_coll = db["guilds"]
    for g in Guild.objects.all():
        members = list(Character.objects.filter(guild=g).values_list("character_name", flat=True))
        guilds_coll.insert_one({"id": g.id, "guild_name": g.guild_name, "members": members})

    # Users: embed transactions and lightweight character refs
    users_coll = db["users"]
    for u in User.objects.all():
        txs = []
        for t in Transaction.objects.filter(user=u):
            txs.append({"id": t.id, "quantity": t.quantity, "cost": t.cost})

        chars = []
        for c in u.characters.all():
            chars.append({"id": c.id, "character_name": c.character_name, "level": c.level})

        users_coll.insert_one({"id": u.id, "username": u.username, "email": u.email, "transactions": txs, "characters": chars})

    # Characters: embed inventory items, skills, quests (with NPC), battles, and guild summary
    chars_coll = db["characters"]
    for c in Character.objects.select_related("user", "guild", "inventory").prefetch_related("skills", "quests__npc", "battles").all():
        # inventory items
        inventory_items = []
        try:
            inv = c.inventory
            # Items that belong to the inventory via Item.inventories
            items_qs = Item.objects.filter(inventories=inv)
            for it in items_qs:
                inventory_items.append(serialize_item(it))
        except Inventory.DoesNotExist:
            inventory_items = []

        # skills
        skills = [serialize_skill(s) for s in c.skills.all()]

        # quests
        quests = [serialize_quest(q) for q in c.quests.select_related("npc").all()]

        # battles
        battles = [serialize_battle(b) for b in c.battles.all()]

        # guild summary
        guild_doc = None
        if c.guild:
            guild_doc = {"id": c.guild.id, "guild_name": c.guild.guild_name}

        user_summary = None
        if c.user:
            user_summary = {"id": c.user.id, "username": c.user.username, "email": c.user.email}

        doc = {
            "id": c.id,
            "character_name": c.character_name,
            "level": c.level,
            "hp": c.hp,
            "mana": c.mana,
            "user": user_summary,
            "guild": guild_doc,
            "inventory": inventory_items,
            "skills": skills,
            "quests": quests,
            "battles": battles,
        }

        chars_coll.insert_one(doc)


def main():
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.environ.get("MONGO_DB", "rpg_mongo")
    # Test SQL connectivity first so we fail fast with actionable hints
    if not test_sql_connection():
        print("Aborting migration due to SQL connection failure.")
        return

    print(f"Connecting to MongoDB {MONGO_URI} DB: {MONGO_DB}")
    client, db = connect_mongo(MONGO_URI, MONGO_DB)

    try:
        migrate_collections(db)
        print("Migration completed. Collections created: items, skills, npcs, quests, battles, guilds, users, characters")
    finally:
        client.close()


if __name__ == "__main__":
    main()
