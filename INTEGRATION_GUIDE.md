# Frontend → Backend → Archia Integration Test

## Setup Instructions

### 1. Backend Server (already running)
```bash
cd src/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend should be running at: http://localhost:8000

### 2. Frontend Development Server
```bash
cd frontend
npm install  # If you haven't already
npm run dev
```

Frontend will start at: http://localhost:5173

## Test the Integration

1. Open browser to http://localhost:5173
2. Type a message in the chat: "Safest route to Ellis Library"
3. The frontend will:
   - Send request to → `http://localhost:8000/api/v1/dispatch`
   - Backend will call → Archia Cloud (`https://registry.archia.app/v1/responses`)
   - Archia Orchestrator → processes with sub-agents
   - Response flows back → Frontend displays AI response

## Architecture Flow

```
User Browser (http://localhost:5173)
    ↓
    POST /api/v1/dispatch with {"message": "..."}
    ↓
Backend API (http://localhost:8000)
    ↓
    POST https://registry.archia.app/v1/responses
    with {"model": "agent:Campus Dispatch Orchestrator", "input": "..."}
    ↓
Archia Cloud
    ├─ Campus Dispatch Orchestrator
    │   ├─ parse_user_intent skill
    │   ├─ plan_route_strategy skill
    │   └─ Agent Orchestration Tools
    │       ├─ Campus Routing Engine (MCP: route_engine)
    │       ├─ Campus risk and prediction engine (MCP: risk_model)
    │       └─ campus context and journalism agent (MCP: rag_search)
    │
    └─ MCP Tools call back to:
        http://localhost:8000/mcp/route
        http://localhost:8000/mcp/risk
        http://localhost:8000/mcp/rag
    ↓
Response flows back up the chain → Frontend displays result
```

## What to Expect

### User Message: "Safest route to Ellis Library"

**AI Response might include:**
- Acknowledgment of the request
- Intent parsing (destination detected)
- Route options generated
- Safety analysis
- Recommended route with explanation

### Troubleshooting

**Frontend can't connect to backend:**
- Check backend is running on port 8000
- Check browser console for CORS errors
- Verify VITE_API_URL in frontend/.env

**Backend can't connect to Archia:**
- Verify ARCHIA_API_KEY in .env
- Check ARCHIA_URL=https://registry.archia.app/v1/responses
- Test with: `python scripts/test_all_agents.py`

**Slow responses:**
- Normal! Archia Orchestrator coordinates multiple agents
- Expect 10-30 seconds for complex routing requests
- Simple greetings respond faster (3-5 seconds)
