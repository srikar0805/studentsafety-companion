import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


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
    archia_api_key: str | None = os.getenv("ARCHIA_API_KEY")
    archia_base_url: str = os.getenv(
        "ARCHIA_BASE_URL",
        "https://registry.archia.app",
    )
    archia_agent_name: str = os.getenv(
        "ARCHIA_AGENT_NAME",
        "Campus Dispatch Orchestrator",
    )
    # Agent names for multi-agent support
    routing_agent_name: str = os.getenv(
        "ROUTING_AGENT_NAME", "Campus Routing Engine"
    )
    risk_agent_name: str = os.getenv(
        "RISK_AGENT_NAME", "Campus risk and prediction engine"
    )
    context_agent_name: str = os.getenv(
        "CONTEXT_AGENT_NAME", "campus context and journalism agent"
    )
    tool_api_key: str | None = os.getenv("TOOL_API_KEY")
    archia_timeout_seconds: int = int(os.getenv("ARCHIA_TIMEOUT_SECONDS", "30"))
    spatial_radius_m: int = int(os.getenv("SPATIAL_RADIUS_M", "500"))
    phone_radius_m: int = int(os.getenv("PHONE_RADIUS_M", "100"))
    temporal_window_days: int = int(os.getenv("TEMPORAL_WINDOW_DAYS", "30"))
    traffic_window_days: int = int(os.getenv("TRAFFIC_WINDOW_DAYS", "90"))
    max_route_alternatives: int = int(os.getenv("MAX_ROUTE_ALTERNATIVES", "2"))

settings = Settings()
