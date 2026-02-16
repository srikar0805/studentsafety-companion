
import os
import psycopg2
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Configuration
DB_CONN = os.getenv("DATABASE_URL")
PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/rag_sources/2025_Annual_Security_Report.pdf"))
MODEL_NAME = 'all-MiniLM-L6-v2'
CHUNK_SIZE = 1000 # Characters
CHUNK_OVERLAP = 200

def get_db_connection():
    conn = psycopg2.connect(DB_CONN)
    return conn

def extract_text_from_pdf(pdf_path):
    print(f"Extracting text from {pdf_path}...")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    print(f"Chunking text ({len(text)} chars)...")
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
    print(f"Created {len(chunks)} chunks.")
    return chunks

def generate_embeddings(chunks):
    print(f"Loading model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    print("Generating embeddings...")
    embeddings = model.encode(chunks)
    return embeddings

def store_embeddings(chunks, embeddings, source="2025_Annual_Security_Report.pdf"):
    print("Storing embeddings in DB...")
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Register vector type if needed, or pass as list
    # pgvector python usually handles numpy arrays or lists automatically if using correct driver/extension mapping
    # But for raw psycopg2, passing list is safest: embedding = %s -> list(emb)
    
    try:
        # Clear existing entries for this source to avoid duplicates on re-run
        cur.execute("DELETE FROM knowledge_base WHERE source = %s", (source,))
        
        sql = "INSERT INTO knowledge_base (content, embedding, source) VALUES (%s, %s, %s)"
        data = []
        for text, emb in zip(chunks, embeddings):
            data.append((text, emb.tolist(), source))
            
        cur.executemany(sql, data)
        conn.commit()
        print(f"Inserted {len(data)} records.")
    except Exception as e:
        print(f"Error storing embeddings: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def run():
    if not os.path.exists(PDF_PATH):
        print(f"Error: PDF not found at {PDF_PATH}")
        return

    text = extract_text_from_pdf(PDF_PATH)
    chunks = chunk_text(text)
    embeddings = generate_embeddings(chunks)
    store_embeddings(chunks, embeddings)
    print("Ingestion Complete.")

if __name__ == "__main__":
    run()
