from .osrm import generate_routes
from .ranking import rank_routes as rank_internal

# Wrap the existing OSRM routing
routing = generate_routes
rank_routes = rank_internal
