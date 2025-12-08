from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models.fields.related import ManyToManyField
from neo4j import GraphDatabase
from django.db import connections, DatabaseError
import os


class Command(BaseCommand):
    help = "Migrates SQL data (Django ORM models) into a Neo4j graph database"

    def handle(self, *args, **options):
        # Read connection config from env vars (with sensible defaults)
        NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
        NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

        # Allow overriding Django DATABASES via env vars (SQL_* or MYSQL_*)
        from django.conf import settings as dj_settings

        # Prefer SQL_* env vars used by other scripts; fall back to MYSQL_* vars used in settings.py
        sql_name = os.environ.get("SQL_NAME") or os.environ.get("MYSQL_NAME")
        sql_user = os.environ.get("SQL_USER") or os.environ.get("MYSQL_USER")
        sql_password = os.environ.get("SQL_PASSWORD") or os.environ.get("MYSQL_PASSWORD")
        sql_host = os.environ.get("SQL_HOST") or os.environ.get("MYSQL_HOST")
        sql_port = os.environ.get("SQL_PORT") or os.environ.get("MYSQL_PORT")

        if any([sql_name, sql_user, sql_password, sql_host, sql_port]):
            default_db = dj_settings.DATABASES.get("default", {}).copy()
            if sql_name:
                default_db["NAME"] = sql_name
            if sql_user:
                default_db["USER"] = sql_user
            if sql_password:
                default_db["PASSWORD"] = sql_password
            if sql_host:
                default_db["HOST"] = sql_host
            if sql_port:
                default_db["PORT"] = sql_port

            dj_settings.DATABASES["default"] = default_db

        # Validate database settings to give clear error messages before queries
        db_conf = dj_settings.DATABASES.get("default", {})
        if not db_conf.get("NAME") or not db_conf.get("HOST"):
            self.stderr.write(self.style.ERROR("Database is not configured for Django ORM access."))
            self.stderr.write("Set environment variables: SQL_NAME/SQL_USER/SQL_PASSWORD/SQL_HOST/SQL_PORT or MYSQL_NAME/MYSQL_USER/... to point to your MySQL instance.")
            return

        self.stdout.write(self.style.NOTICE(f"Connecting to Neo4j: {NEO4J_URI} as {NEO4J_USER}"))
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

        try:
            with driver.session() as session:
                # Start fresh: remove existing nodes/relationships to make runs idempotent
                self.stdout.write("Clearing existing graph data (MATCH (n) DETACH DELETE n)")
                try:
                    session.run("MATCH (n) DETACH DELETE n")
                except Exception as exc:
                    # Common case: authentication failure. Provide clear, actionable guidance.
                    from neo4j.exceptions import AuthError

                    if isinstance(exc, AuthError):
                        self.stderr.write(self.style.ERROR("Neo4j authentication failed."))
                        self.stderr.write("Check that Neo4j is running and that NEO4J_USER/NEO4J_PASSWORD are correct.")
                        self.stderr.write("If you started Neo4j with Docker, use the same password given to NEO4J_AUTH, e.g.: -e NEO4J_AUTH=neo4j/yourpassword")
                        self.stderr.write("To reset the password on a Docker container named 'neo4j':")
                        self.stderr.write("  docker exec -it neo4j bin/neo4j-admin set-initial-password 'NEWPASSWORD' && docker restart neo4j")
                        driver.close()
                        return
                    else:
                        # Re-raise unexpected exceptions so they are visible
                        raise

                # Verify SQL connection before iterating models so we can fail fast with clear guidance
                try:
                    conn = connections["default"]
                    conn.ensure_connection()
                except DatabaseError as db_exc:
                    self.stderr.write(self.style.ERROR("Cannot connect to the SQL database using Django settings."))
                    self.stderr.write(str(db_exc))
                    self.stderr.write("")
                    self.stderr.write("Common fixes:")
                    self.stderr.write(" - Verify environment variables: SQL_NAME/SQL_USER/SQL_PASSWORD/SQL_HOST/SQL_PORT or MYSQL_NAME/... are set correctly")
                    self.stderr.write(" - Ensure the SQL user exists and has privileges for the host (localhost vs 127.0.0.1)")
                    self.stderr.write(" - Test with the MySQL client: mysql -u USER -p -h 127.0.0.1 -P 3306")
                    self.stderr.write(" - If using Docker, check container logs and bind address")
                    driver.close()
                    return

                rpg_models = apps.get_app_config("rpg").get_models()

                # Create uniqueness constraints for sql_id on each model label
                self.stdout.write("Ensuring uniqueness constraints for model labels...")
                for model in rpg_models:
                    label = model.__name__
                    # Neo4j 5+ supports `CREATE CONSTRAINT ... IF NOT EXISTS` syntax
                    constraint_cypher = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.sql_id IS UNIQUE"
                    try:
                        session.run(constraint_cypher)
                    except Exception:
                        # Not critical; continue. Some older servers might differ in syntax.
                        pass

                # First pass: create nodes for every model instance
                for model in rpg_models:
                    label = model.__name__
                    qs = model.objects.all()
                    total = qs.count()
                    if total == 0:
                        self.stdout.write(f"Skipping {label}: no rows")
                        continue

                    self.stdout.write(f"Creating nodes for {label}: {total} rows")

                    for obj in qs:
                        # Gather concrete DB column fields (includes FK id columns)
                        props = {}
                        for field in model._meta.concrete_fields:
                            # skip many-to-many (no concrete DB column)
                            if getattr(field, "many_to_many", False):
                                continue

                            # Use attname to get the actual instance attribute name (FKs -> field_id)
                            attname = getattr(field, "attname", field.name)
                            value = getattr(obj, attname, None)

                            # Normalize common types for Neo4j (datetime -> ISO string, Decimal -> float)
                            if value is not None:
                                try:
                                    # datetimes / dates / times
                                    if hasattr(value, "isoformat"):
                                        value = value.isoformat()
                                    # Decimal -> float
                                    elif "Decimal" in type(value).__name__:
                                        value = float(value)
                                except Exception:
                                    pass

                            props[attname] = value

                        # Always store the primary SQL id separately as `sql_id`
                        props["sql_id"] = obj.pk

                        cypher = f"MERGE (n:{label} {{sql_id: $sql_id}}) SET n += $props"
                        session.run(cypher, sql_id=obj.pk, props=props)

                # Second pass: create relationships for FK and M2M fields
                for model in rpg_models:
                    label = model.__name__
                    qs = model.objects.all()

                    for obj in qs:
                        src_id = obj.id

                        for field in model._meta.get_fields():
                            # skip reverse relationships
                            if field.auto_created and not field.concrete:
                                continue

                            # ForeignKey / OneToOne: create directed relationship from source -> target
                            if field.is_relation and not isinstance(field, ManyToManyField):
                                try:
                                    related_obj = getattr(obj, field.name)
                                except Exception:
                                    related_obj = None

                                if related_obj is None:
                                    continue

                                target_label = field.related_model.__name__
                                tgt_id = related_obj.id

                                rel_name = field.name.upper()
                                cypher = (
                                    "MATCH (a:%s {sql_id: $a_id}), (b:%s {sql_id: $b_id}) "
                                    "MERGE (a)-[r:%s]->(b)"
                                    % (label, target_label, rel_name)
                                )
                                session.run(cypher, a_id=src_id, b_id=tgt_id)

                            # Many-to-Many: create relationships between each pair
                            if isinstance(field, ManyToManyField):
                                related_qs = getattr(obj, field.name).all()
                                target_label = field.related_model.__name__
                                rel_name = field.name.upper()

                                for related in related_qs:
                                    tgt_id = related.id
                                    cypher = (
                                        "MATCH (a:%s {sql_id: $a_id}), (b:%s {sql_id: $b_id}) "
                                        "MERGE (a)-[r:%s]->(b)"
                                        % (label, target_label, rel_name)
                                    )
                                    session.run(cypher, a_id=src_id, b_id=tgt_id)

                self.stdout.write(self.style.SUCCESS("Neo4j migration completed successfully."))

        finally:
            driver.close()
