import logging
from typing import Any, Dict

from .base import BaseAgent
from ..services.rag import retrieve_context
from ..models import LineString
from ..schemas.agent_schemas import ContextAgentOutput, ContextAgentResult

logger = logging.getLogger("campus_dispatch")

class ContextAgent(BaseAgent):
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        routes = input_data.get("routes", [])

        results = []
        for r_dict in routes:
            route_id = r_dict.get("route_id") or r_dict.get("id")
            geometry = LineString(**r_dict["geometry"])
            bbox = self._bbox_from_linestring(geometry)
            query = f"recent safety reports within {bbox}"

            try:
                context_results = retrieve_context(query, top_k=2)
            except Exception:
                logger.exception("RAG lookup failed for route %s", route_id)
                context_results = []

            if context_results:
                summary = self._summarize_context(context_results)
            else:
                summary = "No specific news or recent reports found for this area."

            results.append(
                ContextAgentResult(
                    route_id=route_id,
                    summary=summary,
                )
            )

        return ContextAgentOutput(results=results).model_dump()

    def _bbox_from_linestring(self, line: LineString) -> str:
        lats = [lat for lon, lat in line.coordinates]
        lons = [lon for lon, lat in line.coordinates]
        if not lats or not lons:
            return "unknown"
        return f"{min(lats):.6f},{min(lons):.6f},{max(lats):.6f},{max(lons):.6f}"

    def _summarize_context(self, context_results: list[dict]) -> str:
        top = context_results[0]
        content = (top.get("content") or "").strip()
        if not content:
            return "Recent reports mention activity near this corridor."
        if len(content) > 200:
            content = f"{content[:197]}..."
        return f"Recent reports: {content}"
