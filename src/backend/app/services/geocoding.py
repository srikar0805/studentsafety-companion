from __future__ import annotations

import requests

from ..config import settings
from ..models import Coordinates


class GeocodingError(RuntimeError):
    pass


def geocode_location(query: str) -> Coordinates:
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
    }
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
    if not data:
        raise GeocodingError("No results found")
    item = data[0]
    return Coordinates(latitude=float(item["lat"]), longitude=float(item["lon"]))
