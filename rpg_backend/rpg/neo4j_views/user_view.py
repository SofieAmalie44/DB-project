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
class UserNeo4jView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id=None):
        """Get all users or a single user by ID"""
        conn = Neo4jConnection()
        
        try:
            if user_id:
                query = "MATCH (u:User {sql_id: $id}) RETURN u"
                result = conn.execute_query(query, {"id": int(user_id)})
                
                if not result:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
                
                return Response(result[0]['u'], status=status.HTTP_200_OK)
            else:
                query = "MATCH (u:User) RETURN u ORDER BY u.sql_id"
                result = conn.execute_query(query)
                users = [record['u'] for record in result]
                
                return Response(users, status=status.HTTP_200_OK)
        
        finally:
            conn.close()
