from __future__ import annotations

import logging
import requests

from ..config import settings

logger = logging.getLogger("campus_dispatch")

ARCHIA_RESPONSES_URL = "https://registry.archia.app/v1/responses"


def call_archia(message: str, agent_name: str | None = None) -> dict:
    """
    Call an Archia agent via the /v1/responses endpoint.

    Uses model: "agent:<name>" routing as documented in the Archia API guide.

    Args:
        message: User's natural language query
        agent_name: Name of the agent to invoke (default: from settings)

    Returns:
        dict with "output" key containing the agent's text response
    """
    if not settings.archia_api_key:
        raise RuntimeError("ARCHIA_API_KEY is not configured")

    if agent_name is None:
        agent_name = settings.archia_agent_name

    headers = {
        "Authorization": f"Bearer {settings.archia_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": f"agent:{agent_name}",
        "input": message,
        "stream": False,
    }

    logger.info(f"Calling Archia agent '{agent_name}' at {ARCHIA_RESPONSES_URL}")
    logger.debug(f"Payload: {payload}")

    response = requests.post(
        ARCHIA_RESPONSES_URL,
        json=payload,
        headers=headers,
        timeout=settings.archia_timeout_seconds,
    )

    logger.debug(f"Response Status: {response.status_code}")
    logger.debug(f"Response Body: {response.text[:500]}")

    response.raise_for_status()

    result = response.json()

    # Extract text from the Archia Responses API format
    output_text = _extract_output_text(result)
    if output_text is not None:
        return {"output": output_text}

    # Fallback: return raw output array
    if "output" in result:
        return {"output": result["output"]}

    logger.warning("Unexpected Archia response format, returning raw result")
    return result


def _extract_output_text(response_json: dict) -> str | None:
    """Extract the assistant's text from a /v1/responses reply."""
    for item in response_json.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    return content.get("text")
    return None
