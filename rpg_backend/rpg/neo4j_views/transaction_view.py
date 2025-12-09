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
class TransactionNeo4jView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, transaction_id=None):
        """Get all transactions or a single transaction by ID"""
        conn = Neo4jConnection()
        
        try:
            if transaction_id:
                query = """
                MATCH (t:Transaction {sql_id: $id})
                OPTIONAL MATCH (t)-[:USER]->(u:User)
                OPTIONAL MATCH (t)-[:ITEM]->(i:Item)
                RETURN t, u.username as user_name, i.name as item_name
                """
                result = conn.execute_query(query, {"id": int(transaction_id)})
                
                if not result:
                    return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
                
                data = result[0]
                transaction = data['t']
                transaction['user_name'] = data['user_name']
                transaction['item_name'] = data['item_name']
                
                return Response(transaction, status=status.HTTP_200_OK)
            else:
                query = """
                MATCH (t:Transaction)
                OPTIONAL MATCH (t)-[:USER]->(u:User)
                OPTIONAL MATCH (t)-[:ITEM]->(i:Item)
                RETURN t, u.username as user_name, i.name as item_name
                ORDER BY t.sql_id
                """
                result = conn.execute_query(query)
                
                transactions = []
                for record in result:
                    transaction = record['t']
                    transaction['user_name'] = record['user_name']
                    transaction['item_name'] = record['item_name']
                    transactions.append(transaction)
                
                return Response(transactions, status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def post(self, request):
        """Create a new transaction"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            
            max_id_query = "MATCH (t:Transaction) RETURN coalesce(max(t.sql_id), 0) as max_id"
            max_result = conn.execute_query(max_id_query)
            new_id = max_result[0]['max_id'] + 1
            
            body['sql_id'] = new_id
            
            query = """
            CREATE (t:Transaction)
            SET t = $props
            RETURN t
            """
            result = conn.execute_query(query, {"props": body})
            
            # Create relationships if provided
            if 'user_id' in body:
                rel_query = """
                MATCH (t:Transaction {sql_id: $trans_id})
                MATCH (u:User {sql_id: $user_id})
                MERGE (t)-[:USER]->(u)
                """
                conn.execute_query(rel_query, {"trans_id": new_id, "user_id": body['user_id']})
            
            if 'item_id' in body:
                rel_query = """
                MATCH (t:Transaction {sql_id: $trans_id})
                MATCH (i:Item {sql_id: $item_id})
                MERGE (t)-[:ITEM]->(i)
                """
                conn.execute_query(rel_query, {"trans_id": new_id, "item_id": body['item_id']})
            
            return Response(result[0]['t'], status=status.HTTP_201_CREATED)
        
        finally:
            conn.close()

    def put(self, request, transaction_id):
        """Update a transaction"""
        conn = Neo4jConnection()
        
        try:
            body = request.data.copy()
            body.pop('sql_id', None)
            
            query = """
            MATCH (t:Transaction {sql_id: $id})
            SET t += $props
            RETURN t
            """
            result = conn.execute_query(query, {"id": int(transaction_id), "props": body})
            
            if not result:
                return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(result[0]['t'], status=status.HTTP_200_OK)
        
        finally:
            conn.close()

    def delete(self, request, transaction_id):
        """Delete a transaction"""
        conn = Neo4jConnection()
        
        try:
            query = """
            MATCH (t:Transaction {sql_id: $id})
            DETACH DELETE t
            RETURN count(t) as deleted
            """
            result = conn.execute_query(query, {"id": int(transaction_id)})
            
            if result[0]['deleted'] == 0:
                return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        finally:
            conn.close()
