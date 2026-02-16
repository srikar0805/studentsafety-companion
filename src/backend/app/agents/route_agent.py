import logging
from typing import Any, Dict

from .base import BaseAgent
from ..services.osrm import generate_routes, OsrmError
from ..models import Coordinates
from ..schemas.agent_schemas import RouteAgentOutput, RouteCandidate

logger = logging.getLogger("campus_dispatch")

class RouteAgent(BaseAgent):
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        origin_coords = input_data.get("origin_coords")
        dest_coords = input_data.get("destination_coords")

        if not origin_coords or not dest_coords:
            return {"routes": []}

        if isinstance(origin_coords, dict):
            origin_coords = Coordinates(**origin_coords)
        if isinstance(dest_coords, dict):
            dest_coords = Coordinates(**dest_coords)

        try:
            routes = generate_routes(origin_coords, dest_coords)
        except (OsrmError, Exception):
            logger.info("Routing failed for %s -> %s", origin_coords, dest_coords)
            return {"routes": []}

        output_routes = []
        for route in routes:
            output_routes.append(
                RouteCandidate(
                    route_id=route.id,
                    geometry=route.geometry.model_dump(),
                    edges=[],
                    eta_minutes=route.duration_seconds / 60.0,
                )
            )

        return RouteAgentOutput(routes=output_routes).model_dump()
