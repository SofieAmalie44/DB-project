from django.core.management.base import BaseCommand
from pymongo import MongoClient
from django.apps import apps
from django.db.models.fields.related import ManyToManyField
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Migrates all SQL data (Django ORM models) into MongoDB"

    def handle(self, *args, **kwargs):

        # -------------------------------------
        # CONNECT TO MONGODB
        # -------------------------------------
        client = MongoClient("mongodb://localhost:27017/")
        db = client["rpg_mongo"]  

        self.stdout.write(self.style.NOTICE("Connected to MongoDB"))

        # -------------------------------------
        # FETCH ALL MODELS FROM rpg APP
        # -------------------------------------
        rpg_models = apps.get_app_config("rpg").get_models()

        for model in rpg_models:
            model_name = model.__name__.lower()
            collection = db[model_name]

            if model_name == "inventory":
                self.stdout.write(f"Migrating (embedded): {model_name} ...")

                collection.delete_many({})

                rows = model.objects.all()
                documents = []

                for obj in rows:
                    # base inventory fields
                    doc = {
                        "id": obj.id,
                        "character": obj.character.id
                    }

                    # embed related InventoryItem rows
                    embedded_items = []
                    for ii in obj.items.all(): # reverse relationship from InventoryItem
                        embedded_items.append({
                            "item": ii.item.id,
                            "quantity": ii.quantity
                        })
                    doc["items"] = embedded_items
                    documents.append(doc)
                
                if documents:
                    collection.insert_many(documents)

                self.stdout.write(
                    self.style.SUCCESS(f" {len(documents)} inventory migrated with embedded items")
                )
                continue 

            self.stdout.write(f"Migrating: {model_name} ...")

            # Clear existing data in MongoDB collection
            collection.delete_many({})

            # Fetch SQL rows
            rows = model.objects.all()
            documents = []

            # -------------------------------------
            # CONVERT EACH SQL ROW INTO DOCUMENT
            # -------------------------------------
            for obj in rows:
                doc = {}

                for field in model._meta.get_fields():

                    # Skip reverse relationships, because mongo does not need them
                    if field.auto_created and not field.concrete:
                        continue

                    # Many-to-Many: convert to list of IDs
                    if isinstance(field, ManyToManyField):
                        m2m_ids = list(
                            getattr(obj, field.name).values_list("id", flat=True)
                        )
                        doc[field.name] = m2m_ids
                        continue

                    value = getattr(obj, field.name)

                    # ForeignKey: convert related object to ID
                    if field.is_relation and hasattr(value, "id"):
                        doc[field.name] = value.id
                    else:
                        # Regular field, store as-is
                        doc[field.name] = value

                documents.append(doc)

            # -------------------------------------
            # INSERT INTO MONGODB
            # -------------------------------------
            if documents:
                collection.insert_many(documents)

            self.stdout.write(
                self.style.SUCCESS(f"✔ {len(documents)} rows migrated from {model_name}")
            )


        # -------------------------------------
        # MIGRATE USER TABLE INTO MONGODB
        # -------------------------------------

        self.stdout.write("Migrating: user ...")
        user_collection = db["user"]
        user_collection.delete_many({})

        users = User.objects.all()
        docs = []

        for u in users:
            docs.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "is_staff": u.is_staff,
                "is_superuser": u.is_superuser,
                "date_joined": u.date_joined.isoformat(),
                "last_login": u.last_login.isoformat() if u.last_login else None
            })
        if docs:
            user_collection.insert_many(docs)

        self.stdout.write(self.style.SUCCESS(f" {len(docs)} rows migrated from user"))

        self.stdout.write(self.style.SUCCESS("\n Migration completed successfully!"))