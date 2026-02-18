import sys
from unittest.mock import MagicMock

# Mock heavy/external modules before importing any app modules
for module in ["psycopg", "sentence_transformers", "redis", "geopandas", "osmnx"]:
    sys.modules[module] = MagicMock()

import pytest
import asyncio
from unittest.mock import patch
from src.backend.app.agents.coordinator_agent import CoordinatorAgent
from src.backend.app.agents.intent_agent import IntentAgent
from src.backend.app.models import Coordinates

@pytest.mark.asyncio
async def test_intent_agent():
    # Mock geocode to avoid network call
    with patch("src.backend.app.agents.intent_agent.geocode_location") as mock_geocode:
        mock_geocode.return_value = Coordinates(latitude=38.9483, longitude=-92.3281)
        
        agent = IntentAgent()
        result = await agent.run({"message": "Safest route to Ellis Library at 11 pm"})
        
        assert result["destination"] == "Ellis Library"
        assert result["priority"] == "safety"
        assert result["time"] == "23:00"
        assert result["destination_coords"]["latitude"] == 38.9483

@pytest.mark.asyncio
async def test_coordinator_pipeline():
    # Mocking components to verify orchestration logic
    with patch("src.backend.app.agents.intent_agent.geocode_location") as mock_geocode, \
         patch("src.backend.app.agents.route_agent.generate_routes") as mock_routing, \
         patch("src.backend.app.agents.safety_agent.fetch_incidents") as mock_incidents, \
         patch("src.backend.app.agents.safety_agent.fetch_traffic_stop_count") as mock_traffic, \
         patch("src.backend.app.agents.safety_agent.fetch_emergency_phones") as mock_phones:

        mock_geocode.return_value = Coordinates(latitude=38.9, longitude=-92.3)
        mock_routing.return_value = []
        mock_incidents.return_value = []
        mock_traffic.return_value = 0
        mock_phones.return_value = []

        coordinator = CoordinatorAgent()
        result = await coordinator.run({"message": "Go to Student Union"})

        assert "routes" in result
        assert "explanation" in result
        assert len(result["explanation"]) > 0

if __name__ == "__main__":
    # Simplified manual run with mocks
    async def run_manual():
        print("Running manual test with mocks...")
        with patch("src.backend.app.agents.intent_agent.geocode_location") as mock_geocode, \
             patch("src.backend.app.agents.route_agent.generate_routes") as mock_routing, \
             patch("src.backend.app.agents.safety_agent.fetch_incidents") as mock_incidents, \
             patch("src.backend.app.agents.safety_agent.fetch_traffic_stop_count") as mock_traffic, \
             patch("src.backend.app.agents.safety_agent.fetch_emergency_phones") as mock_phones:

            mock_geocode.return_value = Coordinates(latitude=38.9, longitude=-92.3)
            mock_routing.return_value = []
            mock_incidents.return_value = []
            mock_traffic.return_value = 0
            mock_phones.return_value = []

            coordinator = CoordinatorAgent()
            res = await coordinator.run({"message": "Safest way to the gym at midnight"})
            print(f"Result: {res}")
    
    asyncio.run(run_manual())
