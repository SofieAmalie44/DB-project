from django.core.management.base import BaseCommand
from pymongo import MongoClient
from django.apps import apps
from django.db.models.fields.related import ManyToManyField


class Command(BaseCommand):
    help = "Migrates all SQL data (Django ORM models) into MongoDB"

    def handle(self, *args, **kwargs):

        # -------------------------------------
        # 1. CONNECT TO MONGODB
        # -------------------------------------
        client = MongoClient("mongodb://localhost:27017/")
        db = client["rpg_mongo"]  

        self.stdout.write(self.style.NOTICE("Connected to MongoDB"))

        # -------------------------------------
        # 2. FETCH ALL MODELS FROM rpg APP
        # -------------------------------------
        rpg_models = apps.get_app_config("rpg").get_models()

        for model in rpg_models:
            model_name = model.__name__.lower()
            collection = db[model_name]

            self.stdout.write(f"Migrating: {model_name} ...")

            # Clear existing data in MongoDB collection
            collection.delete_many({})

            # Fetch SQL rows
            rows = model.objects.all()
            documents = []

            # -------------------------------------
            # 3. CONVERT EACH SQL ROW INTO DOCUMENT
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
            # 4. INSERT INTO MONGODB
            # -------------------------------------
            if documents:
                collection.insert_many(documents)

            self.stdout.write(
                self.style.SUCCESS(f"✔ {len(documents)} rows migrated from {model_name}")
            )

        self.stdout.write(self.style.SUCCESS("\n Migration completed successfully!"))
