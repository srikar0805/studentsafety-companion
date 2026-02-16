
import os
import psycopg2
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Configuration
DB_CONN = os.getenv("DATABASE_URL")
MODEL_NAME = 'all-MiniLM-L6-v2'

class RAGRetriever:
    def __init__(self, db_conn=DB_CONN):
        self.conn_str = db_conn
        print(f"Loading model {MODEL_NAME}...")
        self.model = SentenceTransformer(MODEL_NAME)
        
    def search(self, query, top_k=3):
        """
        Embeds query and searches DB for similar chunks.
        """
        # Embed query
        query_emb = self.model.encode(query)
        # Convert to list for pgvector (or string representation if needed, but list usually works with psycopg2+pgvector)
        # Actually, psycopg2 needs explicit casting or string format '[...]' if no adapter registered.
        # Let's use string format '[x,y,z]' to be safe.
        query_emb_str = str(query_emb.tolist())
        
        results = []
        try:
            with psycopg2.connect(self.conn_str) as conn:
                with conn.cursor() as cur:
                    # Cosine distance operator is <=> in pgvector for l2 distance, or <=> for cosine distance? 
                    # vector_l2_ops is <-> (Euclidean). vector_cosine_ops is <=>. 
                    # Use <-> for L2 (Euclidean) which is good for normalized embeddings (MiniLM emits normalized).
                    sql = """
                        SELECT content, source, (embedding <-> %s) as distance
                        FROM knowledge_base
                        ORDER BY distance ASC
                        LIMIT %s
                    """
                    cur.execute(sql, (query_emb_str, top_k))
                    rows = cur.fetchall()
                    for r in rows:
                        results.append({
                            'content': r[0],
                            'source': r[1],
                            'distance': r[2]
                        })
        except Exception as e:
            print(f"Error searching: {e}")
            
        return results

if __name__ == "__main__":
    retriever = RAGRetriever()
    query = "How do I report a crime?"
    print(f"\nQuery: {query}")
    results = retriever.search(query)
    for i, res in enumerate(results):
        print(f"\n--- Result {i+1} (Dist: {res['distance']:.4f}) ---")
        print(res['content'][:200] + "...")
