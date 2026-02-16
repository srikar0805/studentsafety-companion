from __future__ import annotations

import requests

from ..config import settings
from ..models import Coordinates, LineString, Route
from ..utils import to_coordinates


class OsrmError(RuntimeError):
    pass


<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
def generate_routes(origin: Coordinates, destination: Coordinates) -> list[Route]:
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
def generate_routes(
    origin: Coordinates,
    destination: Coordinates,
    alternatives: int | None = None,
) -> list[Route]:
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    base = settings.osrm_base_url.rstrip("/")
    url = (
        f"{base}/route/v1/foot/"
        f"{origin.longitude},{origin.latitude};"
        f"{destination.longitude},{destination.latitude}"
    )
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    params = {
        "alternatives": settings.max_route_alternatives,
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    max_alts = settings.max_route_alternatives
    if alternatives is not None:
        max_alts = max(0, min(int(alternatives), settings.max_route_alternatives))

    params = {
        "alternatives": max_alts,
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        "steps": "true",
        "geometries": "geojson",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != "Ok":
        raise OsrmError(payload.get("message", "OSRM failed"))

    routes = []
    for index, route in enumerate(payload.get("routes", [])):
        geometry = route.get("geometry")
        if not geometry:
            continue
        line = LineString(type="LineString", coordinates=[tuple(p) for p in geometry["coordinates"]])
        distance = float(route.get("distance", 0))
        duration = float(route.get("duration", 0))
        waypoints = [to_coordinates(line.coordinates[0]), to_coordinates(line.coordinates[-1])]
        routes.append(
            Route(
                id=f"route_{index + 1}",
                geometry=line,
                distance_meters=distance,
                duration_seconds=duration,
                waypoints=waypoints,
            )
        )

    if not routes:
        raise OsrmError("No routes available")
    return routes
