from __future__ import annotations

import logging
import requests

from ..config import settings

logger = logging.getLogger("campus_dispatch")


def call_archia(message: str, agent_name: str | None = None) -> dict:
    """
    Call the Archia Responses API with the given message.
    
    Args:
        message: User's natural language query
        agent_name: Name of the agent to invoke (default: from settings)
    
    Returns:
        Parsed response from the agent
    """
    if not settings.archia_api_key:
        raise RuntimeError("ARCHIA_API_KEY is not configured")

    # Use agent name from settings if not provided
    if agent_name is None:
        agent_name = settings.archia_agent_name

    headers = {
        "Authorization": f"Bearer {settings.archia_api_key}",
        "Content-Type": "application/json",
    }
    
    # Archia Cloud uses "model": "agent:<name>" format
    payload = {
        "model": f"agent:{agent_name}",
        "input": message,
        "stream": False
    }
    
    logger.info(f"Calling Archia agent '{agent_name}' at {settings.archia_url}")
    logger.debug(f"Payload: {payload}")
    logger.debug(f"Headers: {dict(headers)}")
    
    response = requests.post(
        settings.archia_url,
        json=payload,
        headers=headers,
        timeout=settings.archia_timeout_seconds,
    )
    
    logger.debug(f"Response Status: {response.status_code}")
    logger.debug(f"Response Headers: {dict(response.headers)}")
    logger.debug(f"Response Body: {response.text[:500]}")
    
    response.raise_for_status()
    
    result = response.json()
    
    # Extract the assistant's response from Archia's output format
    if "output" in result and len(result["output"]) > 0:
        for item in result["output"]:
            if item.get("type") == "message" and item.get("role") == "assistant":
                content = item.get("content", [])
                if content and len(content) > 0:
                    # Return the first text content
                    for part in content:
                        if part.get("type") == "output_text":
                            return {"response": part.get("text", "")}
    
    # Fallback: return the raw result
    logger.warning("Unexpected Archia response format, returning raw result")
    return result
