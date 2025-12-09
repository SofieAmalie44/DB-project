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
class ItemNeo4jView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, item_id=None):
        """Get all items or a single item by ID"""
        conn = Neo4jConnection()
        
        try:
            if item_id:
                query = "MATCH (i:Item {sql_id: $id}) RETURN i"
                result = conn.execute_query(query, {"id": int(item_id)})
                
                if not result:
                    return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
                
                return Response(result[0]['i'], status=status.HTTP_200_OK)
            else:
                query = "MATCH (i:Item) RETURN i ORDER BY i.sql_id"
                result = conn.execute_query(query)
                items = [record['i'] for record in result]
                
                return Response(items, status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def post(self, request):
        """Create a new item"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            
            # Get max ID
            max_id_query = "MATCH (i:Item) RETURN coalesce(max(i.sql_id), 0) as max_id"
            max_result = conn.execute_query(max_id_query)
            new_id = max_result[0]['max_id'] + 1
            
            body['sql_id'] = new_id
            
            query = """
            CREATE (i:Item)
            SET i = $props
            RETURN i
            """
            result = conn.execute_query(query, {"props": body})
            
            return Response(result[0]['i'], status=status.HTTP_201_CREATED)
        
        finally:
            conn.close()

    def put(self, request, item_id):
        """Update an item"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            body.pop('sql_id', None)
            
            query = """
            MATCH (i:Item {sql_id: $id})
            SET i += $props
            RETURN i
            """
            result = conn.execute_query(query, {"id": int(item_id), "props": body})
            
            if not result:
                return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(result[0]['i'], status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def delete(self, request, item_id):
        """Delete an item"""
        conn = Neo4jConnection()
        
        try:
            query = """
            MATCH (i:Item {sql_id: $id})
            DETACH DELETE i
            RETURN count(i) as deleted
            """
            result = conn.execute_query(query, {"id": int(item_id)})
            
            if result[0]['deleted'] == 0:
                return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        finally:
            conn.close()
