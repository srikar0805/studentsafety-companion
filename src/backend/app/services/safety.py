from __future__ import annotations

from collections import Counter
from datetime import datetime

from ..models import Incident, SafetyAnalysis, SafetyTip
from ..utils import risk_level_label


def calculate_base_score(incidents: list[Incident]) -> float:
    return len(incidents) * 10


def apply_temporal_weight(incidents: list[Incident], current_time: datetime) -> float:
    from datetime import timezone
    weighted_score = 0.0
    for incident in incidents:
        inc_date = incident.date
        ct = current_time
        # Ensure both are timezone-aware (UTC)
        if ct.tzinfo is None:
            ct = ct.replace(tzinfo=timezone.utc)
        if inc_date.tzinfo is None:
            inc_date = inc_date.replace(tzinfo=timezone.utc)
        days_ago = (ct - inc_date).days
        if days_ago <= 30:
            weight = 5.0
        elif days_ago <= 90:
            weight = 2.0
        else:
            weight = 1.0
        weighted_score += 10 * weight
    return weighted_score


def apply_time_multiplier(score: float, current_time: datetime) -> float:
    hour = current_time.hour
    if hour >= 22 or hour < 6:
        return score * 2.0
    return score


def apply_infrastructure_adjustments(
    score: float,
    emergency_phones: int,
    lighting_quality: str,
    patrol_frequency: str,
) -> float:
    components = infrastructure_adjustment_components(
        emergency_phones,
        lighting_quality,
        patrol_frequency,
    )
    adjusted = score + components["total_adjustment"]
    return max(0.0, min(100.0, adjusted))


def infrastructure_adjustment_components(
    emergency_phones: int,
    lighting_quality: str,
    patrol_frequency: str,
) -> dict[str, float]:
    phone_adjustment = min(emergency_phones * -5, -15)
    lighting_adjustment = {"good": 0, "moderate": 5, "poor": 10}[lighting_quality]
    patrol_adjustment = {"high": -10, "moderate": 0, "low": 5}[patrol_frequency]
    total_adjustment = phone_adjustment + lighting_adjustment + patrol_adjustment
    return {
        "phone_adjustment": float(phone_adjustment),
        "lighting_adjustment": float(lighting_adjustment),
        "patrol_adjustment": float(patrol_adjustment),
        "total_adjustment": float(total_adjustment),
    }


def patrol_frequency_label(stop_count: int) -> str:
    if stop_count >= 20:
        return "high"
    if stop_count >= 5:
        return "moderate"
    return "low"


def generate_context_aware_tips(incidents: list[Incident], user_mode: str) -> list[SafetyTip]:
    tips: list[SafetyTip] = []
    counts = Counter([incident.type for incident in incidents])

    if user_mode == "student":
        if counts.get("Theft", 0) > 2:
            tips.append(
                SafetyTip(
                    type="advisory",
                    message="High theft reports in this area. Keep jewelry and phones hidden.",
                    trigger_crime="Theft",
                )
            )
        if counts.get("Assault", 0) > 0 or counts.get("Kidnapping", 0) > 0:
            tips.append(
                SafetyTip(
                    type="warning",
                    message="Recent assaults or kidnappings reported. Walk in groups and stay in well-lit areas.",
                    trigger_crime="Assault or Kidnapping",
                )
            )

    if user_mode == "community":
        if counts.get("Burglary", 0) > 2:
            tips.append(
                SafetyTip(
                    type="advisory",
                    message="Residential burglary alerts in this zone. Ensure windows are locked.",
                    trigger_crime="Burglary",
                )
            )

    return tips


def build_concerns(incidents: list[Incident], lighting_quality: str, patrol: str) -> list[str]:
    concerns: list[str] = []
    if incidents:
        concerns.append(f"{len(incidents)} incidents reported nearby")
    if lighting_quality == "poor":
        concerns.append("Poor lighting along the route")
    if patrol == "low":
        concerns.append("Low patrol frequency")
    return concerns


def build_positives(emergency_phones: int, incidents: list[Incident], patrol: str) -> list[str]:
    positives: list[str] = []
    if emergency_phones:
        positives.append(f"{emergency_phones} emergency call boxes along the route")
    if not incidents:
        positives.append("No recent incidents in the area")
    if patrol == "high":
        positives.append("High patrol frequency")
    return positives


def analyze_route_safety(
    incidents: list[Incident],
    emergency_phones: int,
    lighting_quality: str,
    patrol_frequency: str,
    user_mode: str,
    current_time: datetime,
    route_length_m: float = 1.0,  # must be passed in by caller
) -> SafetyAnalysis:
    # Step 1: Compute weighted incidents
    from datetime import timezone
    def compute_weighted_incidents(incidents, time_mult):
        total = 0.0
        for i in incidents:
            ct = current_time
            inc_date = i.date
            # Ensure both are timezone-aware (UTC)
            if ct.tzinfo is None:
                ct = ct.replace(tzinfo=timezone.utc)
            if inc_date.tzinfo is None:
                inc_date = inc_date.replace(tzinfo=timezone.utc)
            days_ago = (ct - inc_date).days
            if days_ago <= 30:
                temporal = 5
            elif days_ago <= 90:
                temporal = 2
            else:
                temporal = 1
            total += 10 * temporal * time_mult
        return total

    hour = current_time.hour
    is_night = hour >= 22 or hour < 6
    time_mult = 2 if is_night else 1
    weighted_incidents = compute_weighted_incidents(incidents, time_mult)
    # Step 2: Density
    density = weighted_incidents / max(route_length_m, 1)
    # Step 3: Normalize
    MAX_DENSITY = 0.08  # tune as needed
    normalized = density / MAX_DENSITY
    risk = normalized * 100

    # Step 4: Infrastructure as percentage modifiers
    if patrol_frequency == "high":
        risk *= 0.8
    if emergency_phones > 0:
        risk *= 0.9
    if lighting_quality == "poor":
        risk *= 1.15

    risk = round(min(risk, 100))

    concerns = build_concerns(incidents, lighting_quality, patrol_frequency)
    positives = build_positives(emergency_phones, incidents, patrol_frequency)

    contributing = []
    if incidents:
        contributing.append(f"{len(incidents)} incidents within radius")
    if emergency_phones:
        contributing.append(f"{emergency_phones} emergency phones nearby")
    if lighting_quality == "moderate":
        contributing.append("Lighting data not available; assuming moderate")

    return SafetyAnalysis(
        risk_score=risk,
        risk_level=risk_level_label(risk),
        incident_count=len(incidents),
        recent_incidents=incidents,
        emergency_phones=emergency_phones,
        lighting_quality=lighting_quality,
        patrol_frequency=patrol_frequency,
        actionable_tips=generate_context_aware_tips(incidents, user_mode),
        concerns=concerns,
        positives=positives,
        contributing_factors=contributing,
    )
