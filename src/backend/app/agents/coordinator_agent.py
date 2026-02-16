import logging
from typing import Any, Dict

from .base import BaseAgent
from .intent_agent import IntentAgent
from .route_agent import RouteAgent
from .safety_agent import SafetyAgent
from .context_agent import ContextAgent
from ..schemas.agent_schemas import AgentFinalResponse, AgentRouteResponse

logger = logging.getLogger("campus_dispatch")

class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.intent_agent = IntentAgent()
        self.route_agent = RouteAgent()
        self.safety_agent = SafetyAgent()
        self.context_agent = ContextAgent()

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            intent = await self.intent_agent.run({"message": input_data.get("message")})
        except Exception:
            logger.exception("Intent agent failed")
            return AgentFinalResponse(
                routes=[],
                explanation="I couldn't understand the request well enough to plan a route.",
            ).model_dump()

        if not intent.get("origin_coords") or not intent.get("destination_coords"):
            return AgentFinalResponse(
                routes=[],
                explanation="I need both an origin and a destination to plan a route.",
            ).model_dump()

        weights = self._select_weights(intent.get("priority", "balanced"))

        try:
            routes_data = await self.route_agent.run({**intent, **weights})
        except Exception:
            logger.exception("Route agent failed")
            routes_data = {"routes": []}

        routes_list = routes_data.get("routes", [])
        if not routes_list:
            return AgentFinalResponse(
                routes=[],
                explanation="I couldn't find any routes to your destination.",
            ).model_dump()

        try:
            safety_data = await self.safety_agent.run(
                {
                    "routes": routes_list,
                    "time": intent.get("time"),
                    "mode": intent.get("mode"),
                }
            )
        except Exception:
            logger.exception("Safety agent failed")
            safety_data = {"results": []}

        try:
            context_data = await self.context_agent.run({"routes": routes_list})
        except Exception:
            logger.exception("Context agent failed")
            context_data = {"results": []}

        safety_results = {r["route_id"]: r for r in safety_data.get("results", [])}
        context_results = {r["route_id"]: r for r in context_data.get("results", [])}

        final_routes = []
        for r_dict in routes_list:
            rid = r_dict["route_id"]
            s_res = safety_results.get(rid, {"incident_probability": 0.5, "confidence": 0.5})
            c_res = context_results.get(rid, {"summary": "No additional context."})

            final_routes.append(
                AgentRouteResponse(
                    route_id=rid,
                    eta=r_dict["eta_minutes"],
                    risk=s_res["incident_probability"],
                    confidence=s_res["confidence"],
                    summary=c_res["summary"],
                    geometry=r_dict["geometry"],
                )
            )

        priority = intent.get("priority", "balanced")
        if priority == "safety":
            final_routes.sort(key=lambda x: x.risk)
        elif priority == "speed":
            final_routes.sort(key=lambda x: x.eta)
        else:
            final_routes.sort(key=lambda x: (x.risk * 0.6) + (x.eta / 30.0 * 0.4))

        explanation = (
            f"I've found {len(final_routes)} routes. The recommended path is optimized for {priority}."
        )
        if final_routes:
            explanation += f" {final_routes[0].summary}"

        return AgentFinalResponse(routes=final_routes, explanation=explanation).model_dump()

    def _select_weights(self, priority: str) -> Dict[str, float]:
        if priority == "safety":
            return {"risk_weight": 0.7, "time_weight": 0.3}
        if priority == "speed":
            return {"risk_weight": 0.3, "time_weight": 0.7}
        return {"risk_weight": 0.5, "time_weight": 0.5}
