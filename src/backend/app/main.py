from __future__ import annotations

import logging
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .cache import get_cache
from .config import settings
from .models import ErrorResponse, Recommendation, RouteRequest, RoutesResponse
from .services.geocoding import GeocodingError, geocode_location
from .services.osrm import OsrmError, generate_routes
from .services.queries import (
    fetch_emergency_phones,
    fetch_incidents,
    fetch_traffic_stop_count,
    is_within_campus,
)
from .services.ranking import build_ranked_routes, rank_routes
from .services.safety import analyze_route_safety, patrol_frequency_label
from .utils import parse_request_time

app = FastAPI(title="Campus Dispatch Copilot API")
cache = get_cache()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/routes", response_model=RoutesResponse)
def get_routes(request: RouteRequest):
    request_id = str(uuid.uuid4())

    try:
        current_time = parse_request_time(request.time)
    except Exception:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error_code="INVALID_TIME",
                user_message="I could not understand the time you provided.",
                suggestions=["Use ISO format like 2026-02-15T23:00:00Z or 'current'."],
            ).model_dump(),
        )

    try:
        origin = (
            geocode_location(request.origin)
            if isinstance(request.origin, str)
            else request.origin
        )
        destination = (
            geocode_location(request.destination)
            if isinstance(request.destination, str)
            else request.destination
        )
    except GeocodingError:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error_code="GEOCODING_FAILED",
                user_message="I could not find that location.",
                suggestions=["Try a nearby landmark or a full address."],
            ).model_dump(),
        )

    if not is_within_campus(origin) or not is_within_campus(destination):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error_code="OUT_OF_BOUNDS",
                user_message="One of the locations is outside the campus boundary.",
                suggestions=["Pick a campus building or address within campus."],
            ).model_dump(),
        )

    cache_key = (
        f"route:{origin.latitude},{origin.longitude}:"
        f"{destination.latitude},{destination.longitude}"
    )

    cached_routes = None if request.force_refresh else cache.get(cache_key)
    if cached_routes:
        routes = [item for item in cached_routes]
    else:
        try:
            routes = generate_routes(origin, destination)
        except OsrmError:
            return JSONResponse(
                status_code=502,
                content=ErrorResponse(
                    error_code="OSRM_UNAVAILABLE",
                    user_message="Routing service is temporarily unavailable.",
                    suggestions=["Try again in a few minutes."],
                ).model_dump(),
            )
        cache.set(cache_key, [route.model_dump() for route in routes], ttl_seconds=3600)
        routes = routes

    if cached_routes:
        from .models import Route

        routes = [Route(**item) for item in cached_routes]

    analyses = []
    all_incidents = []
    all_phones = []

    for route in routes:
        incidents = fetch_incidents(route.geometry, settings.spatial_radius_m, settings.temporal_window_days)
        stop_count = fetch_traffic_stop_count(route.geometry, settings.spatial_radius_m, settings.traffic_window_days)
        patrol = patrol_frequency_label(stop_count)
        phones = fetch_emergency_phones(route.geometry, settings.phone_radius_m)

        analysis = analyze_route_safety(
            incidents=incidents,
            emergency_phones=len(phones),
            lighting_quality="moderate",
            patrol_frequency=patrol,
            user_mode=request.user_mode,
            current_time=current_time,
        )

        analyses.append(analysis)
        all_incidents.extend(incidents)
        all_phones.extend(phones)

    ranked_indices = rank_routes(
        routes,
        analyses,
        request.priority,
        current_hour=current_time.hour,
    )
    ranked_routes = build_ranked_routes(routes, analyses, ranked_indices)

    primary = ranked_routes[0]
    comparison = build_comparison_text(primary, ranked_routes)
    explanation = primary.explanation

    recommendation = Recommendation(
        routes=ranked_routes,
        primary_recommendation=primary,
        explanation=explanation,
        comparison=comparison,
    )

    return RoutesResponse(
        request_id=request_id,
        recommendation=recommendation,
        incidents=dedupe_incidents(all_incidents),
        emergency_phones=dedupe_points(all_phones),
    )


def build_comparison_text(primary, ranked_routes):
    if len(ranked_routes) < 2:
        return "This is the only available route."
    alternative = ranked_routes[1]
    return (
        f"The recommended route is about {primary.time_tradeoff_minutes} minutes "
        f"slower but {primary.safety_improvement_percent}% safer than the fastest path."
    )


def dedupe_incidents(incidents):
    seen = set()
    unique = []
    for incident in incidents:
        if incident.id in seen:
            continue
        seen.add(incident.id)
        unique.append(incident)
    return unique


def dedupe_points(points):
    seen = set()
    unique = []
    for point in points:
        key = (round(point.latitude, 6), round(point.longitude, 6))
        if key in seen:
            continue
        seen.add(key)
        unique.append(point)
    return unique


@app.exception_handler(Exception)
def handle_unexpected_error(request, exc):
    logger.exception("Unhandled error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            user_message="Something went wrong on our side.",
            suggestions=["Try again in a moment."],
        ).model_dump(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
