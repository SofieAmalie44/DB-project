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
class GuildNeo4jView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, guild_id=None):
        """Get all guilds or a single guild by ID"""
        conn = Neo4jConnection()
        
        try:
            if guild_id:
                query = "MATCH (g:Guild {sql_id: $id}) RETURN g"
                result = conn.execute_query(query, {"id": int(guild_id)})
                
                if not result:
                    return Response({"error": "Guild not found"}, status=status.HTTP_404_NOT_FOUND)
                
                return Response(result[0]['g'], status=status.HTTP_200_OK)
            else:
                query = "MATCH (g:Guild) RETURN g ORDER BY g.sql_id"
                result = conn.execute_query(query)
                guilds = [record['g'] for record in result]
                
                return Response(guilds, status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def post(self, request):
        """Create a new guild"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            
            max_id_query = "MATCH (g:Guild) RETURN coalesce(max(g.sql_id), 0) as max_id"
            max_result = conn.execute_query(max_id_query)
            new_id = max_result[0]['max_id'] + 1
            
            body['sql_id'] = new_id
            
            query = """
            CREATE (g:Guild)
            SET g = $props
            RETURN g
            """
            result = conn.execute_query(query, {"props": body})
            
            return Response(result[0]['g'], status=status.HTTP_201_CREATED)
        
        finally:
            conn.close()

    def put(self, request, guild_id):
        """Update a guild"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            body.pop('sql_id', None)
            
            query = """
            MATCH (g:Guild {sql_id: $id})
            SET g += $props
            RETURN g
            """
            result = conn.execute_query(query, {"id": int(guild_id), "props": body})
            
            if not result:
                return Response({"error": "Guild not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(result[0]['g'], status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def delete(self, request, guild_id):
        """Delete a guild"""
        conn = Neo4jConnection()
        
        try:
            query = """
            MATCH (g:Guild {sql_id: $id})
            DETACH DELETE g
            RETURN count(g) as deleted
            """
            result = conn.execute_query(query, {"id": int(guild_id)})
            
            if result[0]['deleted'] == 0:
                return Response({"error": "Guild not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({"status": "Guild deleted"}, status=status.HTTP_200_OK)
        
        finally:
            conn.close()
