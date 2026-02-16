
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONN = os.getenv("DATABASE_URL")

def apply_schema():
    engine = create_engine(DB_CONN)
    with engine.connect() as conn:
        print("Enable vector extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        
        print("Creating knowledge_base table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding vector(384),
                source VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        print("Creating HNSW index...")
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_rag_embedding ON knowledge_base USING hnsw (embedding vector_l2_ops);"))
        
        conn.commit()
        print("RAG Schema Applied.")

if __name__ == "__main__":
    apply_schema()
