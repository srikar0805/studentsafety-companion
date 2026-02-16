"""
Diagnostic Report - Archia Integration

Request Details (from backend logs):
====================================
✅ Payload: {'agent': 'Campus Dispatch Orchestrator', 'input': 'Hello'}
✅ Headers: Authorization: Bearer ask_6eHsr1hT6lMuNUREnDEWYwlsj2_ri_ubxavyRFzR87Q=
✅ Content-Type: application/json
✅ URL: https://api.archia.app/v1/responses

Response Details:
=================
❌ Status: 464 Client Error
❌ Body: Empty (0 bytes)
❌ Server: awselb/2.0 (AWS Load Balancer)

Analysis:
=========
The request is reaching AWS infrastructure but being rejected by the load balancer
with a 464 status code BEFORE it gets to Archia's application servers.

464 is NOT a standard HTTP status code. It's custom to Archia.

Possible Issues:
================

1. **API Key Permission Issue** (MOST LIKELY)
   - The API key works in the console UI but may not have API access enabled
   - Console UI uses different auth than programmatic API access
   - Solution: Check API key permissions in Archia console
   
2. **Missing Required Headers**
   - Some APIs require additional headers like:
     - X-Api-Version
     - X-Workspace-Id
     - User-Agent
   - Solution: Check Archia API documentation for required headers
   
3. **Workspace Context Missing**
   - Console knows your workspace context, API calls might need it explicit
   - May need to include workspace ID in URL or headers
   - Solution: Check if endpoint should be /v1/workspaces/{id}/responses
   
4. **Deployment/Region Issue**
   - console.archia.app might use different backend than api.archia.app
   - May need different endpoint URL
   - Solution: Check Archia docs for correct API endpoint

Actions to Take:
================

□ 1. In Archia Console → Settings → API Keys
     - Verify the key has "API Access" permission (not just "Console Access")
     - Generate a NEW key specifically for API use if needed
     
□ 2. Check Archia Documentation
     - Look for "Programmatic API Access" or "API Authentication"
     - Verify the exact endpoint URL for responses
     - Check for required headers
     
□ 3. Contact Archia Support
     - Provide them with:
       * Status code: 464
       * Endpoint: https://api.archia.app/v1/responses  
       * Agent name: "Campus Dispatch Orchestrator"
       * Request timestamp: Feb 16, 2026 05:13:16 GMT
       * API key prefix: ask_6eHsr1hT6l
     - Ask: "Why is my API call getting 464 when console works?"
     
□ 4. Try Alternative Endpoints (if documented)
     - /v1/agents/{id}/invoke
     - /v1/chat/completions
     - /v1/inference

Comparison with Working Console:
=================================
Works in Console ✅  →  Fails via API ❌

This strongly suggests AUTH/PERMISSION issue rather than agent configuration.

The agent itself is fine. The API key likely needs different permissions.
"""

print(__doc__)
print("\n" + "="*60)
print("RECOMMENDATION: Check API Key Permissions")
print("="*60)
print("""
Go to console.archia.app → Settings → API Keys

Look for these settings on your key:
- [ ] Console Access  (probably enabled)
- [ ] API Access      (probably DISABLED) ← Enable this
- [ ] Agent Execution (probably needed)  ← Enable this too

Or create a NEW API key with full permissions.
""")
