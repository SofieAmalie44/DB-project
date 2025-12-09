from django.core.management.base import BaseCommand
from neo4j import GraphDatabase
from django.apps import apps
from django.db.models.fields.related import ManyToManyField
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = "Migrates SQL data (Django ORM models) into a Neo4j graph database"

    def handle(self, *args, **kwargs):
        # Connect to Neo4j
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        try:
            with driver.session() as session:
                self.stdout.write(self.style.NOTICE("Connected to Neo4j"))
                
                # Clear existing data
                session.run("MATCH (n) DETACH DELETE n")
                
                # Get all RPG models
                rpg_models = apps.get_app_config("rpg").get_models()
                
                # Create nodes for each model
                for model in rpg_models:
                    label = model.__name__
                    
                    try:
                        rows = model.objects.all()
                        total = rows.count()
                    except Exception as e:
                        self.stdout.write(f"Skipping {label}: {str(e)[:50]}")
                        continue
                    
                    if total == 0:
                        continue
                    
                    self.stdout.write(f"Migrating: {label} ...")
                    
                    for obj in rows:
                        props = {"sql_id": obj.id}
                        
                        for field in model._meta.get_fields():
                            if field.auto_created and not isinstance(field, ManyToManyField):
                                continue
                            
                            if isinstance(field, ManyToManyField):
                                continue
                            
                            field_name = field.name
                            try:
                                value = getattr(obj, field_name)
                            except:
                                value = None
                            
                            if value is not None:
                                if hasattr(value, 'isoformat'):
                                    value = value.isoformat()
                                elif hasattr(value, 'id'):
                                    props[f"{field_name}_id"] = value.id
                                    continue
                                else:
                                    props[field_name] = value
                            else:
                                props[field_name] = value
                        
                        cypher = f"CREATE (n:{label}) SET n = $props"
                        session.run(cypher, props=props)
                    
                    self.stdout.write(self.style.SUCCESS(f"✔ {total} rows migrated from {label}"))
                
                # Migrate User table
                self.stdout.write("Migrating: User ...")
                users = User.objects.all()
                docs = []
                
                for u in users:
                    props = {
                        "sql_id": u.id,
                        "username": u.username,
                        "email": u.email,
                        "first_name": u.first_name,
                        "last_name": u.last_name,
                        "is_staff": u.is_staff,
                        "is_superuser": u.is_superuser,
                        "date_joined": u.date_joined.isoformat(),
                        "last_login": u.last_login.isoformat() if u.last_login else None
                    }
                    cypher = "CREATE (n:User) SET n = $props"
                    session.run(cypher, props=props)
                
                user_count = User.objects.count()
                self.stdout.write(self.style.SUCCESS(f"✔ {user_count} rows migrated from User"))
                
                self.stdout.write("Creating relationships...")
                rel_count = 0
                
                # Reload models for relationship creation
                rpg_models = apps.get_app_config("rpg").get_models()
                
                for model in rpg_models:
                    label = model.__name__
                    
                    try:
                        rows = model.objects.all()
                    except:
                        continue
                    
                    if rows.count() == 0:
                        continue
                    
                    for obj in rows:
                        src_id = obj.id
                        
                        for field in model._meta.get_fields():
                            if field.auto_created and not isinstance(field, ManyToManyField):
                                continue
                            
                            # ForeignKey relationships
                            if field.is_relation and not isinstance(field, ManyToManyField):
                                try:
                                    related_obj = getattr(obj, field.name, None)
                                    if related_obj is not None:
                                        target_label = field.related_model.__name__
                                        tgt_id = related_obj.id
                                        rel_name = field.name.upper()
                                        
                                        cypher = f"""
                                        MATCH (a:{label} {{sql_id: $a_id}})
                                        MATCH (b:{target_label} {{sql_id: $b_id}})
                                        MERGE (a)-[:{rel_name}]->(b)
                                        """
                                        session.run(cypher, a_id=src_id, b_id=tgt_id)
                                        rel_count += 1
                                except:
                                    pass
                            
                            # Many-to-Many relationships
                            elif isinstance(field, ManyToManyField):
                                try:
                                    related_manager = getattr(obj, field.name, None)
                                    if related_manager:
                                        related_qs = related_manager.all()
                                        if related_qs.exists():
                                            target_label = field.related_model.__name__
                                            rel_name = field.name.upper()
                                            
                                            for related in related_qs:
                                                tgt_id = related.id
                                                cypher = f"""
                                                MATCH (a:{label} {{sql_id: $a_id}})
                                                MATCH (b:{target_label} {{sql_id: $b_id}})
                                                MERGE (a)-[:{rel_name}]->(b)
                                                """
                                                session.run(cypher, a_id=src_id, b_id=tgt_id)
                                                rel_count += 1
                                except:
                                    pass
                
                self.stdout.write(self.style.SUCCESS(f"✔ {rel_count} relationships created"))
        
        finally:
            driver.close()