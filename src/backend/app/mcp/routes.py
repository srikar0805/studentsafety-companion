"""
MCP Tool Endpoints

These are called BY Archia agents when they use tools.
NOT called by frontend directly.
"""
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, HTTPException
from ..models import Coordinates, LineString
from ..services.osrm import generate_routes, OsrmError
from ..services.safety import analyze_route_safety, patrol_frequency_label
from ..services.queries import (
    fetch_incidents,
    fetch_traffic_stop_count,
    fetch_emergency_phones,
)
from ..services.rag import retrieve_context
from ..config import settings
from ..utils import parse_request_time
from .schemas import RouteToolInput, RiskToolInput, RAGToolInput, TrafficToolInput

logger = logging.getLogger("campus_dispatch")

router = APIRouter(prefix="/mcp", tags=["MCP Tools"])


@router.post("/route")
async def route_tool(input_data: RouteToolInput):
    """
    MCP Tool: Generate routes between origin and destination.
    Called by Archia's Routing Agent.
    """
    try:
        origin = Coordinates(**input_data.origin)
        destination = Coordinates(**input_data.destination)
        
        routes = generate_routes(origin, destination)
        
        output_routes = []
        for route in routes:
            output_routes.append({
                "route_id": route.id,
                "geometry": route.geometry.model_dump(),
                "distance_meters": route.distance_meters,
                "eta_minutes": route.duration_seconds / 60.0,
                "edges": [],  # Could extract from OSRM if needed
            })
        
        return {"routes": output_routes}
    
    except OsrmError as e:
        logger.error(f"Routing failed: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.exception("Route tool failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk")
async def risk_tool(input_data: RiskToolInput):
    """
    MCP Tool: Analyze safety/risk for routes.
    Called by Archia's Risk & Prediction Agent.
    """
    try:
        time_str = input_data.time
        user_mode = input_data.mode
        
        try:
            current_time = parse_request_time(time_str)
        except Exception:
            current_time = datetime.now(timezone.utc)
        
        results = []
        for r_dict in input_data.routes:
            route_id = r_dict.get("route_id") or r_dict.get("id")
            geometry = LineString(**r_dict["geometry"])
            
            try:
                incidents = fetch_incidents(
                    geometry,
                    radius_m=settings.spatial_radius_m,
                    days_back=settings.temporal_window_days,
                )
                traffic_stops = fetch_traffic_stop_count(
                    geometry,
                    radius_m=settings.spatial_radius_m,
                    days_back=settings.traffic_window_days,
                )
                emergency_phones = fetch_emergency_phones(
                    geometry,
                    radius_m=settings.phone_radius_m,
                )
            except Exception:
                logger.exception(f"Safety data lookup failed for route {route_id}")
                incidents = []
                traffic_stops = 0
                emergency_phones = []
            
            patrol = patrol_frequency_label(traffic_stops)
            
            analysis = analyze_route_safety(
                incidents=incidents,
                emergency_phones=len(emergency_phones),
                lighting_quality="moderate",
                patrol_frequency=patrol,
                user_mode=user_mode,
                current_time=current_time,
            )
            
            results.append({
                "route_id": route_id,
                "incident_probability": analysis.risk_score / 100.0,
                "confidence": 0.85,
                "risk_score": analysis.risk_score,
                "risk_level": analysis.risk_level,
                "incident_count": analysis.incident_count,
            })
        
        return {"results": results}
    
    except Exception as e:
        logger.exception("Risk tool failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag")
async def rag_tool(input_data: RAGToolInput):
    """
    MCP Tool: Retrieve context from RAG system.
    Called by Archia's Context & Journalism Agent.
    """
    try:
        results = retrieve_context(input_data.query, top_k=input_data.top_k)
        
        return {
            "results": results if results else [],
            "count": len(results) if results else 0,
        }
    
    except Exception as e:
        logger.exception("RAG tool failed")
        # Don't fail hard on RAG errors
        return {"results": [], "count": 0, "error": str(e)}


@router.post("/traffic")
async def traffic_tool(input_data: TrafficToolInput):
    """
    MCP Tool: Get traffic stop data near a route.
    """
    try:
        geometry = LineString(**input_data.geometry)
        
        stop_count = fetch_traffic_stop_count(
            geometry,
            radius_m=input_data.radius_m,
            days_back=input_data.days_back,
        )
        
        patrol = patrol_frequency_label(stop_count)
        
        return {
            "stop_count": stop_count,
            "patrol_frequency": patrol,
        }
    
    except Exception as e:
        logger.exception("Traffic tool failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def mcp_health():
    """MCP health check endpoint"""
    return {"status": "ok", "service": "mcp_tools"}
