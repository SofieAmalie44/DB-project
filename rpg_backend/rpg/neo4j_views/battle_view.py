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
class BattleNeo4jView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, battle_id=None):
        """Get all battles or a single battle by ID"""
        conn = Neo4jConnection()
        
        try:
            if battle_id:
                query = """
                MATCH (b:Battle {sql_id: $id})
                OPTIONAL MATCH (b)-[:CHARACTER]->(c:Character)
                RETURN b, c.character_name as character_name
                """
                result = conn.execute_query(query, {"id": int(battle_id)})
                
                if not result:
                    return Response({"error": "Battle not found"}, status=status.HTTP_404_NOT_FOUND)
                
                data = result[0]
                battle = data['b']
                battle['character_name'] = data['character_name']
                
                return Response(battle, status=status.HTTP_200_OK)
            else:
                query = """
                MATCH (b:Battle)
                OPTIONAL MATCH (b)-[:CHARACTER]->(c:Character)
                RETURN b, c.character_name as character_name
                ORDER BY b.sql_id
                """
                result = conn.execute_query(query)
                
                battles = []
                for record in result:
                    battle = record['b']
                    battle['character_name'] = record['character_name']
                    battles.append(battle)
                
                return Response(battles, status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def post(self, request):
        """Create a new battle"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            
            max_id_query = "MATCH (b:Battle) RETURN coalesce(max(b.sql_id), 0) as max_id"
            max_result = conn.execute_query(max_id_query)
            new_id = max_result[0]['max_id'] + 1
            
            body['sql_id'] = new_id
            body.setdefault('xp', 0)
            body.setdefault('money', 0)
            
            query = """
            CREATE (b:Battle)
            SET b = $props
            RETURN b
            """
            result = conn.execute_query(query, {"props": body})
            
            # Create character relationship if provided
            if 'character_id' in body:
                rel_query = """
                MATCH (b:Battle {sql_id: $battle_id})
                MATCH (c:Character {sql_id: $char_id})
                MERGE (b)-[:CHARACTER]->(c)
                """
                conn.execute_query(rel_query, {"battle_id": new_id, "char_id": body['character_id']})
            
            return Response(result[0]['b'], status=status.HTTP_201_CREATED)
        
        finally:
            conn.close()

    def put(self, request, battle_id):
        """Update a battle"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            body.pop('sql_id', None)
            
            query = """
            MATCH (b:Battle {sql_id: $id})
            SET b += $props
            RETURN b
            """
            result = conn.execute_query(query, {"id": int(battle_id), "props": body})
            
            if not result:
                return Response({"error": "Battle not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(result[0]['b'], status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def delete(self, request, battle_id):
        """Delete a battle"""
        conn = Neo4jConnection()
        
        try:
            query = """
            MATCH (b:Battle {sql_id: $id})
            DETACH DELETE b
            RETURN count(b) as deleted
            """
            result = conn.execute_query(query, {"id": int(battle_id)})
            
            if result[0]['deleted'] == 0:
                return Response({"error": "Battle not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        finally:
            conn.close()
