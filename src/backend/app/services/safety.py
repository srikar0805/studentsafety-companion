from __future__ import annotations

from collections import Counter
from datetime import datetime

from ..models import Incident, SafetyAnalysis, SafetyTip
from ..utils import risk_level_label


def calculate_base_score(incidents: list[Incident]) -> float:
    return len(incidents) * 10


def apply_temporal_weight(incidents: list[Incident], current_time: datetime) -> float:
    weighted_score = 0.0
    for incident in incidents:
        days_ago = (current_time - incident.date).days
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
    phone_adjustment = min(emergency_phones * -5, -15)
    lighting_adjustment = {"good": 0, "moderate": 5, "poor": 10}[lighting_quality]
    patrol_adjustment = {"high": -10, "moderate": 0, "low": 5}[patrol_frequency]
    adjusted = score + phone_adjustment + lighting_adjustment + patrol_adjustment
    return max(0.0, min(100.0, adjusted))


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
                    message="Critical: High risk incidents reported. Avoid walking alone here.",
                    trigger_crime="Personal Safety",
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
) -> SafetyAnalysis:
    base = calculate_base_score(incidents)
    temporal = apply_temporal_weight(incidents, current_time)
    time_adjusted = apply_time_multiplier(temporal, current_time)
    final_score = apply_infrastructure_adjustments(
        time_adjusted,
        emergency_phones,
        lighting_quality,
        patrol_frequency,
    )

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
        risk_score=final_score,
        risk_level=risk_level_label(final_score),
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
