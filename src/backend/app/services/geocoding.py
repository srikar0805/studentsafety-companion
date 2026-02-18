from __future__ import annotations

import requests

from ..config import settings
from ..models import Coordinates


class GeocodingError(RuntimeError):
    pass


# Mizzou campus bounding box for biasing results
_CAMPUS_VIEWBOX = "-92.345,38.935,-92.310,38.955"
_CAMPUS_SUFFIX = ", Columbia, MO"


def geocode_location(query: str) -> Coordinates:
    """
    Geocode a location string to coordinates.

    Short or ambiguous queries are biased toward the University of Missouri
    campus area by appending ', Columbia, MO' and using a viewbox.
    """
    biased_query = query
    use_viewbox = False

    # If query doesn't already mention a city/state, add campus context
    lowered = query.lower()
    has_location_context = any(
        kw in lowered for kw in ["columbia", "missouri", "mizzou", ", mo", ", il", ", ca"]
    )
    if not has_location_context:
        biased_query = query + _CAMPUS_SUFFIX
        use_viewbox = True

    params = {
        "q": biased_query,
        "format": "json",
        "limit": 1,
    }
    if use_viewbox:
        params["viewbox"] = _CAMPUS_VIEWBOX
        params["bounded"] = 0  # prefer but don't strictly limit

    headers = {
        "User-Agent": settings.geocoder_user_agent,
    }
    response = requests.get(
        f"{settings.geocoder_base_url}/search",
        params=params,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    # If biased query fails, try the original query
    if not data and biased_query != query:
        params["q"] = query
        params.pop("viewbox", None)
        params.pop("bounded", None)
        response = requests.get(
            f"{settings.geocoder_base_url}/search",
            params=params,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

    if not data:
        raise GeocodingError(f"No results found for '{query}'")

    item = data[0]
    return Coordinates(latitude=float(item["lat"]), longitude=float(item["lon"]))
