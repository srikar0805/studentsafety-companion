
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.routing.router import Router
from src.rag.retrieve import RAGRetriever
from src.api.models import RouteRequest, RouteResponse, ChatRequest, ChatResponse
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Campus Safety Companion API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
router_engine = None
rag_engine = None

@app.on_event("startup")
def startup_event():
    global router_engine, rag_engine
    print("Initializing Routing Engine...")
    # main.py is in src/api/
    # graph is in hackathon3/ (project root)
    # studentsafety-companion/src/api -> ../../.. -> hackathon3/
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    graph_path = os.path.join(project_root, "campus_network.graphml")
    
    if os.path.exists(graph_path):
        router_engine = Router(graph_path)
    else:
        print(f"Warning: Graph not found at {graph_path}")
        
    print("Initializing RAG Engine...")
    rag_engine = RAGRetriever()
    print("Startup Complete.")

@app.get("/health")
def health_check():
    return {"status": "ok", "router": router_engine is not None}

@app.post("/navigate", response_model=RouteResponse)
def navigate(req: RouteRequest):
    if not router_engine:
        raise HTTPException(status_code=503, detail="Router not initialized")
    
    path = router_engine.get_route(req.origin, req.dest, mode=req.mode)
    if not path:
        raise HTTPException(status_code=404, detail="No path found")
    
    # Calculate stats
    # Convert node path to coords
    coords = router_engine.route_to_coords(path)
    
    # Calculate distance/risk
    total_len = 0
    total_risk = 0
    path_len = len(path)
    
    if path_len > 1:
        for u, v in zip(path[:-1], path[1:]):
            data = router_engine.graph.get_edge_data(u, v)[0]
            total_len += data.get('length', 0)
            total_risk += data.get('risk_factor', 1.0)
        avg_risk = total_risk / (path_len - 1)
    else:
        avg_risk = 0
        
    return {
        "path": coords,
        "distance": total_len,
        "risk_score": avg_risk
    }

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG not initialized")
    
    results = rag_engine.search(req.query, top_k=3)
    
    # Basic RAG: Return top chunk as answer
    # Ideally, feed to LLM here.
    if not results:
        return {"answer": "I couldn't find any information on that.", "citations": []}
    
    answer = results[0]['content']
    citations = [r['source'] for r in results]
    
    return {"answer": answer, "citations": citations}

@app.get("/map/assets")
def get_assets():
    # Return safety assets as GeoJSON FeatureCollection
    DB_CONN = os.getenv("DATABASE_URL")
    try:
        conn = psycopg2.connect(DB_CONN)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT asset_type, description, ST_AsGeoJSON(location_geo) as geometry FROM safety_assets")
        rows = cur.fetchall()
        
        features = []
        for r in rows:
            features.append({
                "type": "Feature",
                "geometry": json.loads(r['geometry']),
                "properties": {
                    "type": r['asset_type'],
                    "description": r['description']
                }
            })
            
        return {"type": "FeatureCollection", "features": features}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
