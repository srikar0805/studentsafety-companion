# Integrating Archia Agents into the Campus Dispatch Copilot Web App

This document describes how to connect the Archia-hosted multi-agent system to the Campus Dispatch Copilot local web application.

The web app communicates with Archia through a backend proxy layer using secure API keys.

---

## 1. Architecture Overview


Frontend (React / UI)
|
v
Backend API (FastAPI)
|
v
Archia Agent Runtime
|
v
Campus Dispatch Orchestrator Agent
|
v
Routing / Risk / Context Agents
|
v
Tools → Backend Services → Databases / APIs


The frontend never talks directly to Archia.

---

## 2. Prerequisites

- Archia workspace with:
  - Tools created
  - Skills created
  - Four agents created
- An Archia API key
- Backend running (FastAPI recommended)

---

## 3. Store Archia API Key

Create environment variable:


ARCHIA_API_KEY=ask_xxxxxxxxxxxxxxxxx


Never commit this key to GitHub.

---

## 4. Backend: Archia Client

Create file:


src/backend/app/clients/archia_client.py


```python
import os
import requests

ARCHIA_URL = "https://api.archia.ai/v1/agents/CampusDispatchOrchestrator/invoke"
API_KEY = os.getenv("ARCHIA_API_KEY")

def call_archia(message: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {"input": message}
    response = requests.post(ARCHIA_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
5. Backend: API Endpoint

Modify main.py:

from fastapi import FastAPI, HTTPException
from app.clients.archia_client import call_archia

app = FastAPI()

@app.post("/api/v1/dispatch")
async def dispatch(req: dict):
    try:
        result = call_archia(req["message"])
        return result["output"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
6. Frontend: Call Backend Endpoint
async function getRoute(message) {
  const res = await fetch("/api/v1/dispatch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });

  return await res.json();
}
7. Expected Response Format
{
  "routes": [
    {
      "geometry": [...],
      "eta": 14.2,
      "risk": 0.028,
      "confidence": 0.85,
      "summary": "Better lighting and fewer incidents."
    }
  ]
}
8. Rendering in Frontend

Draw route geometry on map

Display ETA

Display risk percentage

Display explanation text

9. Testing
Test Archia Directly
POST https://api.archia.ai/v1/agents/CampusDispatchOrchestrator/invoke
{
  "input": "Safest route to Ellis Library"
}
Test Backend
curl -X POST http://localhost:8000/api/v1/dispatch \
-H "Content-Type: application/json" \
-d '{"message":"Safest route to Ellis Library"}'
10. Error Handling

If Archia unavailable → return friendly error

Log failures

Do not expose API keys

11. Security Best Practices

Store API key in environment variable

Use HTTPS

Add rate limiting on backend

12. Checklist

 Archia agents created

 API key saved

 Backend client created

 Endpoint added

 Frontend connected

 End-to-end test passed

13. Result

The Campus Dispatch Copilot web app is now connected to the Archia-hosted agentic AI system and can generate intelligent, safety-aware routes from natural language queries.