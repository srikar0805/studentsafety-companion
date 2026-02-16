"""
🔍 ARCHIA CONNECTION DIAGNOSTICS
================================

Current Configuration:
- Agent Name: "Campus Dispatch Orchestrator"
- API Key: ask_6eHsr1hT6lMuNURE...
- Endpoint: https://api.archia.app/v1/responses
- Payload Format: {"agent": "...", "input": "..."}

✅ VERIFIED:
- Backend is sending correct agent name (not CampusDispatchOrchestrator)
- Payload format matches Archia docs (agent key, not model)
- MCP endpoints implemented at /mcp/route, /mcp/risk, etc.

❌ STILL FAILING:
- Getting 464 Client Error with empty response body

🎯 NEXT STEPS TO CHECK IN ARCHIA CONSOLE:

1. Verify Agent Status
   - Go to console.archia.app
   - Click "Agents" in sidebar
   - Find "Campus Dispatch Orchestrator"
   - Check if it's ENABLED (not disabled/archived)

2. Verify API Key
   - Go to Settings/API Keys
   - Confirm key starts with: ask_6eHsr1hT6lMuNURE...
   - Check if it's active (not revoked)
   - Verify it has access to the agent

3. Verify Exact Agent Name
   - In Agents list, click on the orchestrator
   - Copy the EXACT name (case-sensitive)
   - Confirm it's: "Campus Dispatch Orchestrator"
   - NOT: "campus dispatch orchestrator" or "Campus dispatch orchestrator"

4. Check MCP Tool URLs in Archia Console
   - Each tool should point to: http://localhost:8000/mcp/<tool>
   - route_engine → http://localhost:8000/mcp/route
   - risk_model → http://localhost:8000/mcp/risk
   - rag_search → http://localhost:8000/mcp/rag
   - traffic_api → http://localhost:8000/mcp/traffic

5. Test with Different Agent (if available)
   - Try calling one of the sub-agents directly:
     - "Campus Routing Engine"
     - "Campus risk and prediction engine"
   - Update .env: ARCHIA_AGENT_NAME=Campus Routing Engine
   - Restart backend and test

🔧 ALTERNATIVE: Use Archia Cloud Console Test
   - Go to console.archia.app
   - Click "Campus Dispatch Orchestrator"
   - Use the built-in "Test" or "Run" feature
   - Send input: "Safest route to Ellis Library"
   - See if it works in console
   - If YES → API key or workspace issue
   - If NO → Agent configuration issue

📋 CHECKLIST:
□ Agent is enabled in console
□ API key is valid and active
□ Agent name matches EXACTLY (case-sensitive)
□ Tool URLs configured in console (if required)
□ Tools are enabled for the sub-agents
"""
print(__doc__)
