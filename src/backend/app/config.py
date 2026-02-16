from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/campus_safety",
    )
    redis_url: str | None = os.getenv("REDIS_URL")
    osrm_base_url: str = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")
    geocoder_base_url: str = os.getenv(
        "GEOCODER_BASE_URL", "https://nominatim.openstreetmap.org"
    )
    geocoder_user_agent: str = os.getenv(
        "GEOCODER_USER_AGENT", "campus-dispatch-copilot/1.0"
    )
    spatial_radius_m: int = int(os.getenv("SPATIAL_RADIUS_M", "500"))
    phone_radius_m: int = int(os.getenv("PHONE_RADIUS_M", "100"))
    temporal_window_days: int = int(os.getenv("TEMPORAL_WINDOW_DAYS", "30"))
    traffic_window_days: int = int(os.getenv("TRAFFIC_WINDOW_DAYS", "90"))
    max_route_alternatives: int = int(os.getenv("MAX_ROUTE_ALTERNATIVES", "2"))


settings = Settings()
