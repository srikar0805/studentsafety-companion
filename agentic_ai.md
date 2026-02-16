# Campus Dispatch Copilot  
## Agent Architecture & Configuration

---

## Overview

Campus Dispatch Copilot uses a 4-agent architecture:

1. Campus Dispatch Orchestrator  
2. Campus Routing Engine  
3. Campus Risk & Prediction Engine  
4. Campus Context & Journalism Agent  

The Orchestrator coordinates all other agents using agent orchestration tools.

---

## 1. Campus Dispatch Orchestrator

### Purpose
Central planner and decision-maker. Interprets user intent, selects routing strategy, delegates tasks, evaluates results, and produces final response.

### Model
Opus 4.6 (Private)  
Fallback: Opus 4.5 → GPT-5.2 → GPT-4.1

### System-Level Tools
- Agent Orchestration Tools (enabled)
- Ephemeral Store Tools (enabled)

### MCP Tools
None

### Skills
- parse_user_intent  
- plan_route_strategy  
- evaluate_route_safety  
- rank_routes  
- adjust_weights  
- generate_explanation  

### System Prompt

You are the Campus Dispatch Copilot Orchestrator.

Responsibilities:

Understand user intent.

Decide routing strategy.

Delegate tasks to specialized agents.

Evaluate returned routes.

Ensure safety-aware optimization.

Provide clear explanations.

Rules:

Use structured JSON when delegating.

Prefer safety when user asks for safest routes.

Retry with adjusted weights if all routes are unsafe.

Return 2–3 route options with ETA, risk probability, and explanation.


---

## 2. Campus Routing Engine

### Purpose
Generates candidate routes using multi-objective A*.

### Model
Sonnet 4.5 (Private)

### MCP Tools
- route_engine  
- traffic_api  

### Skills
None

### System Prompt

You are a routing specialist.

Given origin, destination, risk_weight, and time_weight:
Call route_engine.
Return candidate routes with edge IDs and estimated time.
Return JSON only.


### Input
```json
{
  "origin": [lat, lon],
  "destination": [lat, lon],
  "risk_weight": 0.7,
  "time_weight": 0.3
}
Output
{
  "routes": [
    {
      "route_id": "R1",
      "edge_ids": [1,2,3],
      "eta_minutes": 12.4
    }
  ]
}
3. Campus Risk & Prediction Engine
Purpose

Computes safety probabilities, ETA variance, and shuttle delay.

Model

Sonnet 4 (Private)

MCP Tools

risk_model

shuttle_eta

traffic_api

Skills

None

System Prompt
You compute quantitative predictions for candidate routes.

For each route:
- Call risk_model
- Call shuttle_eta if needed
- Call traffic_api for variance

Return JSON only with:
route_id,
incident_probability,
eta_variance_minutes,
shuttle_delay_minutes,
confidence_score
Output
{
  "results": [
    {
      "route_id": "R1",
      "incident_probability": 0.03,
      "eta_variance_minutes": 3.2,
      "shuttle_delay_minutes": null,
      "confidence_score": 0.86
    }
  ]
}
4. Campus Context & Journalism Agent
Purpose

Retrieves and summarizes relevant news and police reports for route context.

Model

Haiku 4.5 (Private)

MCP Tools

rag_search

Skills

None

System Prompt
For each route:
- Call rag_search with bounding box.
- Summarize safety-related findings in 1–2 sentences.

Return JSON only with:
route_id,
summary,
sources_count,
recency_days
Output
{
  "results": [
    {
      "route_id": "R1",
      "summary": "Two theft reports near Providence Rd in past 30 days.",
      "sources_count": 2,
      "recency_days": 14
    }
  ]
}
Execution Flow

User → Orchestrator
Orchestrator → Routing Agent
Orchestrator → Risk Agent
Orchestrator → RAG Agent
Orchestrator → Evaluate & Respond

Agent → Tool Mapping
Agent	Tools
Orchestrator	Agent Orchestration, Ephemeral Store
Routing Engine	route_engine, traffic_api
Risk Engine	risk_model, shuttle_eta, traffic_api
RAG Agent	rag_search
Notes

Start with 4 agents only.

Add more agents only if scaling.

Keep routing and ML outside LLMs.