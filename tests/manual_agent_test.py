import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# Mock heavy modules
for module in ["psycopg", "sentence_transformers", "redis", "geopandas", "osmnx"]:
    sys.modules[module] = MagicMock()

# Set PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.backend.app.agents.coordinator_agent import CoordinatorAgent
from src.backend.app.models import Coordinates, Incident
from datetime import datetime, timezone

async def run_comprehensive_test():
    coordinator = CoordinatorAgent()
    
    print("\n" + "="*50)
    print("STARTING COMPREHENSIVE AGENT TEST")
    print("="*50)

    # Test Case 1: Safety-focused request
    test_message = "Safest route from Rollins Hall to Ellis Library at 11pm"
    print(f"\nTEST CASE 1: {test_message}")
    
    with patch("src.backend.app.agents.intent_agent.geocode_location") as mock_geocode, \
         patch("src.backend.app.agents.route_agent.generate_routes") as mock_routing, \
         patch("src.backend.app.agents.safety_agent.fetch_incidents") as mock_incidents, \
         patch("src.backend.app.agents.safety_agent.fetch_traffic_stop_count") as mock_traffic, \
         patch("src.backend.app.agents.safety_agent.fetch_emergency_phones") as mock_phones, \
         patch("src.backend.app.agents.context_agent.retrieve_context") as mock_rag:

        # Set up mocks
        mock_geocode.side_effect = lambda q: Coordinates(latitude=38.94, longitude=-92.32)
        
        # Mock a route
        mock_route = MagicMock()
        mock_route.id = "route_123"
        mock_route.duration_seconds = 600
        mock_route.geometry = MagicMock()
        mock_route.geometry.model_dump.return_value = {"type": "LineString", "coordinates": [[-92.32, 38.94], [-92.33, 38.95]]}
        mock_routing.return_value = [mock_route]
        
        # Mock safety data
        mock_incidents.return_value = [
            Incident(
                id="inc_1",
                type="Theft",
                location=Coordinates(latitude=38.941, longitude=-92.321),
                date=datetime.now(timezone.utc),
                description="Theft reported near library"
            )
        ]
        mock_traffic.return_value = 5 # Good patrol
        mock_phones.return_value = [Coordinates(latitude=38.941, longitude=-92.321)]
        
        # Mock RAG
        mock_rag.return_value = [{"content": "Ellis Library has high security presence during finals week."}]

        result = await coordinator.run({"message": test_message})
        
        print("\nCOORDINATOR RESPONSE:")
        print(f"Explanation: {result['explanation']}")
        print(f"Routes found: {len(result['routes'])}")
        if result['routes']:
            route = result['routes'][0]
            print(f"Route ID: {route['route_id']}")
            print(f"ETA: {route['eta']:.1f} mins")
            print(f"Risk Score: {route['risk']*100:.1f}%")
            print(f"Summary: {route['summary']}")

    print("\n" + "="*50)
    print("COMPREHENSIVE TEST COMPLETE")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
