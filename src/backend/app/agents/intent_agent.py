import logging
import re
from typing import Any, Dict

from .base import BaseAgent
from ..services.geocoding import geocode_location, GeocodingError
from ..schemas.agent_schemas import IntentOutput

logger = logging.getLogger("campus_dispatch")

class IntentAgent(BaseAgent):
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        message = input_data.get("message", "")

        destination = self._extract_destination(message)
        origin_query = self._extract_origin(message) or input_data.get("origin")
        priority = self._extract_priority(message)
        time_value = self._extract_time(message)

        dest_coords = self._safe_geocode(destination)
        origin_coords = self._safe_geocode(origin_query) if origin_query else None

        output = IntentOutput(
            destination=destination or "Unknown",
            origin=origin_query,
            priority=priority,
            time=time_value,
            mode=input_data.get("mode", "student"),
            destination_coords=dest_coords,
            origin_coords=origin_coords,
        )

        return output.model_dump()

    def _extract_destination(self, message: str) -> str:
        match = re.search(
            r"(?:to|towards)\s+(.+?)(?:\s+at\s+\d|$)",
            message,
            flags=re.IGNORECASE,
        )
        return match.group(1).strip() if match else ""

    def _extract_origin(self, message: str) -> str:
        match = re.search(
            r"from\s+([A-Za-z][A-Za-z\s']+)\s+(?:to|towards)",
            message,
            flags=re.IGNORECASE,
        )
        return match.group(1).strip() if match else ""

    def _extract_priority(self, message: str) -> str:
        lowered = message.lower()
        if any(w in lowered for w in ["safe", "safest", "safety", "avoid"]):
            return "safety"
        if any(w in lowered for w in ["fast", "fastest", "quick", "short"]):
            return "speed"
        return "balanced"

    def _extract_time(self, message: str) -> str:
        time_match = re.search(
            r"(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)?",
            message,
        )
        if not time_match:
            return "current"

        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridiem = (time_match.group(3) or "").lower()

        if meridiem:
            if meridiem == "pm" and hour < 12:
                hour += 12
            if meridiem == "am" and hour == 12:
                hour = 0

        if hour > 23 or minute > 59:
            return "current"

        return f"{hour:02d}:{minute:02d}"

    def _safe_geocode(self, query: str | None):
        if not query:
            return None
        try:
            return geocode_location(query)
        except GeocodingError:
            logger.info("Geocoding failed for '%s'", query)
            return None
