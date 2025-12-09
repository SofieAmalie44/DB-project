from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from neo4j import GraphDatabase
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os


class Neo4jConnection:
    def __init__(self):
        self.uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.environ.get("NEO4J_USER", "neo4j")
        self.password = os.environ.get("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def close(self):
        self.driver.close()
    
    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]


@method_decorator(csrf_exempt, name="dispatch")
class CharacterNeo4jView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, char_id=None):
        """Get all characters or a single character by ID"""
        conn = Neo4jConnection()
        
        try:
            if char_id:
                query = """
                MATCH (c:Character {sql_id: $id})
                OPTIONAL MATCH (c)-[:USER]->(u:User)
                OPTIONAL MATCH (c)-[:GUILD]->(g:Guild)
                OPTIONAL MATCH (c)-[:SKILLS]->(s:Skill)
                OPTIONAL MATCH (c)-[:QUESTS]->(q:Quest)
                RETURN c, 
                       u.username as user_name,
                       g.guild_name as guild_name,
                       collect(DISTINCT s.name) as skills,
                       collect(DISTINCT q.title) as quests
                """
                result = conn.execute_query(query, {"id": int(char_id)})
                
                if not result:
                    return Response({"error": "Character not found"}, status=status.HTTP_404_NOT_FOUND)
                
                data = result[0]
                character = data['c']
                character['user_name'] = data['user_name']
                character['guild_name'] = data['guild_name']
                character['skills'] = data['skills']
                character['quests'] = data['quests']
                
                return Response(character, status=status.HTTP_200_OK)
            else:
                query = """
                MATCH (c:Character)
                OPTIONAL MATCH (c)-[:USER]->(u:User)
                OPTIONAL MATCH (c)-[:GUILD]->(g:Guild)
                RETURN c, u.username as user_name, g.guild_name as guild_name
                ORDER BY c.sql_id
                """
                result = conn.execute_query(query)
                
                characters = []
                for record in result:
                    char = record['c']
                    char['user_name'] = record['user_name']
                    char['guild_name'] = record['guild_name']
                    characters.append(char)
                
                return Response(characters, status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def post(self, request):
        """Create a new character"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            
            # Get the highest sql_id and increment
            max_id_query = "MATCH (c:Character) RETURN coalesce(max(c.sql_id), 0) as max_id"
            max_result = conn.execute_query(max_id_query)
            new_id = max_result[0]['max_id'] + 1
            
            body['sql_id'] = new_id
            body.setdefault('level', 1)
            body.setdefault('hp', 100)
            body.setdefault('mana', 50)
            body.setdefault('xp', 0)
            body.setdefault('gold', 0)
            
            query = """
            CREATE (c:Character)
            SET c = $props
            RETURN c
            """
            result = conn.execute_query(query, {"props": body})
            
            # Create relationships if provided
            if 'user_id' in body:
                rel_query = """
                MATCH (c:Character {sql_id: $char_id})
                MATCH (u:User {sql_id: $user_id})
                MERGE (c)-[:USER]->(u)
                """
                conn.execute_query(rel_query, {"char_id": new_id, "user_id": body['user_id']})
            
            if 'guild_id' in body:
                rel_query = """
                MATCH (c:Character {sql_id: $char_id})
                MATCH (g:Guild {sql_id: $guild_id})
                MERGE (c)-[:GUILD]->(g)
                """
                conn.execute_query(rel_query, {"char_id": new_id, "guild_id": body['guild_id']})
            
            return Response(result[0]['c'], status=status.HTTP_201_CREATED)
        
        finally:
            conn.close()

    def put(self, request, char_id):
        """Update a character"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            
            # Remove immutable field
            body.pop('sql_id', None)
            
            query = """
            MATCH (c:Character {sql_id: $id})
            SET c += $props
            RETURN c
            """
            result = conn.execute_query(query, {"id": int(char_id), "props": body})
            
            if not result:
                return Response({"error": "Character not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(result[0]['c'], status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def delete(self, request, char_id):
        """Delete a character"""
        conn = Neo4jConnection()
        
        try:
            query = """
            MATCH (c:Character {sql_id: $id})
            DETACH DELETE c
            RETURN count(c) as deleted
            """
            result = conn.execute_query(query, {"id": int(char_id)})
            
            if result[0]['deleted'] == 0:
                return Response({"error": "Character not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({"status": "Character deleted"}, status=status.HTTP_200_OK)
        
        finally:
            conn.close()
