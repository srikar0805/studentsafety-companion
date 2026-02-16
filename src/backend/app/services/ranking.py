from __future__ import annotations

from dataclasses import dataclass

from ..models import RankedRoute, Route, SafetyAnalysis


@dataclass(frozen=True)
class RankedInput:
    route: Route
    analysis: SafetyAnalysis


def rank_routes(
    routes: list[Route],
    analyses: list[SafetyAnalysis],
    priority: str,
    current_hour: int,
) -> list[int]:
    pairs = list(zip(routes, analyses, strict=True))

    if current_hour >= 22 or current_hour < 6:
        if priority != "speed":
            priority = "safety"

    if priority == "safety":
        ordered = sorted(pairs, key=lambda pair: pair[1].risk_score)
    elif priority == "speed":
        ordered = sorted(pairs, key=lambda pair: pair[0].duration_seconds)
    else:
        risks = [pair[1].risk_score for pair in pairs]
        durations = [pair[0].duration_seconds for pair in pairs]
        max_risk = max(risks) or 1
        max_duration = max(durations) or 1

        def score(pair):
            normalized_risk = pair[1].risk_score / max_risk
            normalized_duration = pair[0].duration_seconds / max_duration
            return (normalized_risk * 0.6) + (normalized_duration * 0.4)

        ordered = sorted(pairs, key=score)

    return [routes.index(pair[0]) for pair in ordered]


def build_ranked_routes(
    routes: list[Route],
    analyses: list[SafetyAnalysis],
    ranked_indices: list[int],
) -> list[RankedRoute]:
    fastest = min(routes, key=lambda route: route.duration_seconds)
    fastest_analysis = analyses[routes.index(fastest)]

    ranked_routes: list[RankedRoute] = []
    for rank, index in enumerate(ranked_indices, start=1):
        route = routes[index]
        analysis = analyses[index]
        duration_minutes = int(round(route.duration_seconds / 60.0))
        time_tradeoff = int(round((route.duration_seconds - fastest.duration_seconds) / 60.0))

        risk_diff = fastest_analysis.risk_score - analysis.risk_score
        if fastest_analysis.risk_score <= 0:
            safety_improvement = 0
        else:
            safety_improvement = int(round((risk_diff / fastest_analysis.risk_score) * 100))

        explanation = build_route_explanation(route, analysis, time_tradeoff)

        ranked_routes.append(
            RankedRoute(
                rank=rank,
                route=route,
                safety_analysis=analysis,
                duration_minutes=duration_minutes,
                distance_meters=int(round(route.distance_meters)),
                safety_improvement_percent=safety_improvement,
                time_tradeoff_minutes=time_tradeoff,
                explanation=explanation,
            )
        )

    return ranked_routes


def build_route_explanation(
    route: Route,
    analysis: SafetyAnalysis,
    time_tradeoff: int,
) -> str:
    risk_label = analysis.risk_level
    incident_text = f"{analysis.incident_count} incidents" if analysis.incident_count else "no recent incidents"
    phone_text = f"{analysis.emergency_phones} emergency phones" if analysis.emergency_phones else "no emergency phones"
    tradeoff = ""
    if time_tradeoff > 0:
        tradeoff = f" It adds about {time_tradeoff} minutes compared to the fastest option."

    return (
        f"This route is rated {risk_label}. It passes {incident_text} and has {phone_text}."
        f"{tradeoff}"
    )
