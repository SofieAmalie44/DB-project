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
class QuestNeo4jView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, quest_id=None):
        """Get all quests or a single quest by ID"""
        conn = Neo4jConnection()
        
        try:
            if quest_id:
                query = """
                MATCH (q:Quest {sql_id: $id})
                OPTIONAL MATCH (q)-[:NPC]->(n:NPC)
                RETURN q, n.name as npc_name
                """
                result = conn.execute_query(query, {"id": int(quest_id)})
                
                if not result:
                    return Response({"error": "Quest not found"}, status=status.HTTP_404_NOT_FOUND)
                
                data = result[0]
                quest = data['q']
                quest['npc_name'] = data['npc_name']
                
                return Response(quest, status=status.HTTP_200_OK)
            else:
                query = """
                MATCH (q:Quest)
                OPTIONAL MATCH (q)-[:NPC]->(n:NPC)
                RETURN q, n.name as npc_name
                ORDER BY q.sql_id
                """
                result = conn.execute_query(query)
                
                quests = []
                for record in result:
                    quest = record['q']
                    quest['npc_name'] = record['npc_name']
                    quests.append(quest)
                
                return Response(quests, status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def post(self, request):
        """Create a new quest"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            
            max_id_query = "MATCH (q:Quest) RETURN coalesce(max(q.sql_id), 0) as max_id"
            max_result = conn.execute_query(max_id_query)
            new_id = max_result[0]['max_id'] + 1
            
            body['sql_id'] = new_id
            
            query = """
            CREATE (q:Quest)
            SET q = $props
            RETURN q
            """
            result = conn.execute_query(query, {"props": body})
            
            # Create NPC relationship if provided
            if 'npc_id' in body:
                rel_query = """
                MATCH (q:Quest {sql_id: $quest_id})
                MATCH (n:NPC {sql_id: $npc_id})
                MERGE (q)-[:NPC]->(n)
                """
                conn.execute_query(rel_query, {"quest_id": new_id, "npc_id": body['npc_id']})
            
            return Response(result[0]['q'], status=status.HTTP_201_CREATED)
        
        finally:
            conn.close()

    def put(self, request, quest_id):
        """Update a quest"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            body.pop('sql_id', None)
            
            query = """
            MATCH (q:Quest {sql_id: $id})
            SET q += $props
            RETURN q
            """
            result = conn.execute_query(query, {"id": int(quest_id), "props": body})
            
            if not result:
                return Response({"error": "Quest not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(result[0]['q'], status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def delete(self, request, quest_id):
        """Delete a quest"""
        conn = Neo4jConnection()
        
        try:
            query = """
            MATCH (q:Quest {sql_id: $id})
            DETACH DELETE q
            RETURN count(q) as deleted
            """
            result = conn.execute_query(query, {"id": int(quest_id)})
            
            if result[0]['deleted'] == 0:
                return Response({"error": "Quest not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        finally:
            conn.close()
