import logging
from datetime import datetime, timezone
from typing import Any, Dict

from .base import BaseAgent
from ..config import settings
from ..services.safety import analyze_route_safety, patrol_frequency_label
from ..services.queries import (
    fetch_incidents,
    fetch_traffic_stop_count,
    fetch_emergency_phones,
)
from ..models import LineString
from ..schemas.agent_schemas import SafetyAgentOutput, SafetyAgentResult
from ..utils import parse_request_time

logger = logging.getLogger("campus_dispatch")

class SafetyAgent(BaseAgent):
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        routes = input_data.get("routes", [])
        time_str = input_data.get("time", "current")
        user_mode = input_data.get("mode", "student")

        try:
            current_time = parse_request_time(time_str)
        except Exception:
            current_time = datetime.now(timezone.utc)

        results = []
        for r_dict in routes:
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
                logger.exception("Safety data lookup failed for route %s", route_id)
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

            results.append(
                SafetyAgentResult(
                    route_id=route_id,
                    incident_probability=analysis.risk_score / 100.0,
                    confidence=0.85,
                )
            )

        return SafetyAgentOutput(results=results).model_dump()
