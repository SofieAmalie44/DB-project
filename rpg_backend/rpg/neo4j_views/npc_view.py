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
class NPCNeo4jView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, npc_id=None):
        """Get all NPCs or a single NPC by ID"""
        conn = Neo4jConnection()
        
        try:
            if npc_id:
                query = "MATCH (n:NPC {sql_id: $id}) RETURN n"
                result = conn.execute_query(query, {"id": int(npc_id)})
                
                if not result:
                    return Response({"error": "NPC not found"}, status=status.HTTP_404_NOT_FOUND)
                
                return Response(result[0]['n'], status=status.HTTP_200_OK)
            else:
                query = "MATCH (n:NPC) RETURN n ORDER BY n.sql_id"
                result = conn.execute_query(query)
                npcs = [record['n'] for record in result]
                
                return Response(npcs, status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def post(self, request):
        """Create a new NPC"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            
            max_id_query = "MATCH (n:NPC) RETURN coalesce(max(n.sql_id), 0) as max_id"
            max_result = conn.execute_query(max_id_query)
            new_id = max_result[0]['max_id'] + 1
            
            body['sql_id'] = new_id
            
            query = """
            CREATE (n:NPC)
            SET n = $props
            RETURN n
            """
            result = conn.execute_query(query, {"props": body})
            
            return Response(result[0]['n'], status=status.HTTP_201_CREATED)
        
        finally:
            conn.close()

    def put(self, request, npc_id):
        """Update an NPC"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            body.pop('sql_id', None)
            
            query = """
            MATCH (n:NPC {sql_id: $id})
            SET n += $props
            RETURN n
            """
            result = conn.execute_query(query, {"id": int(npc_id), "props": body})
            
            if not result:
                return Response({"error": "NPC not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(result[0]['n'], status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def delete(self, request, npc_id):
        """Delete an NPC"""
        conn = Neo4jConnection()
        
        try:
            query = """
            MATCH (n:NPC {sql_id: $id})
            DETACH DELETE n
            RETURN count(n) as deleted
            """
            result = conn.execute_query(query, {"id": int(npc_id)})
            
            if result[0]['deleted'] == 0:
                return Response({"error": "NPC not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        finally:
            conn.close()
