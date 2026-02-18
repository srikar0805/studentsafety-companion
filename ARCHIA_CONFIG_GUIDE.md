# Archia Agent Configuration Guide

This guide provides the exact configuration needed in the Archia console to support location disambiguation and transportation mode selection.

## Overview

The navigation enhancement adds two new conversation flows:
1. **Disambiguation Flow**: When users request categories (dorm, library, etc.), present location options
2. **Transportation Mode Selection**: Extract and use walking, biking, driving, or bus routing

---

## Agent Tool Updates

### 1. Update Campus Dispatch Agent Prompt

Add these new capabilities to the agent system prompt:

```
ENHANCED CAPABILITIES:

Location Disambiguation:
- When users request general categories (dorm, library, dining, etc.), you will receive a disambiguation response
- Present the location options to the user and ask them to choose
- Example categories: dorm, library, dining hall, recreation center, parking

Transportation Modes:
- Users can specify how they want to travel: walking, biking, driving, or taking the bus
- Extract transportation mode from messages containing keywords:
  - Walking: walk, walking, on foot
  - Biking: bike, biking, cycle, cycling
  - Driving: drive, driving, car
  - Bus: bus, shuttle, tiger line, transit
- Default to walking if no mode is specified

Response Types:
You may receive different response types from the backend:
1. "disambiguation" - Present location options and ask user to choose
2. "routes" - Display routes as normal
```

### 2. Add Category Keywords to Training Data

In the Archia console, add these example queries to help the agent recognize categories:

**Category Detection Examples:**
```
User: "Take me to a dorm"
→ Category: dorm

User: "Where's a library"
→ Category: library

User: "Find me food"
→ Category: dining

User: "I need to park"
→ Category: parking

User: "Where's the gym"
→ Category: recreation
```

**Transportation Mode Examples:**
```
User: "Bike to Ellis Library"
→ Mode: bike

User: "I want to drive to the rec center"
→ Mode: car

User: "Can I take the bus to the Student Center"
→ Mode: bus

User: "Walk to Jesse Hall safely"
→ Mode: walk (default)
```

---

## Response Handling Configuration

### Disambiguation Response Format

When the backend returns `response_type: "disambiguation"`, the agent should:

1. **Present the question** from the response
2. **List all location options** with names
3. **Wait for user selection**

Example agent response:
```
I found several dorms on campus. Which one would you like to go to?

1. Hatch Hall
2. Mark Twain Hall
3. College Avenue Hall
4. Gateway Hall
5. Lathrop Hall

Please select a number or tell me the name.
```

### Follow-Up Handling

After user selects a location:
- Send a new request with the specific location name
- Include the original transportation mode and priority
- Proceed with normal route generation

---

## API Integration Updates

### Request Format

The agent should send requests in this format:

```json
{
  "message": "Take me to a dorm by bike",
  "origin": "Student Center",  // Optional, can be coordinates
  "mode": "student"             // student or community
}
```

### Response Formats

**Disambiguation Response:**
```json
{
  "response_type": "disambiguation",
  "category": "dorm",
  "question": "Which dorm would you like to go to?",
  "options": [
    {
      "name": "Hatch Hall",
      "address": "Columbia, MO",
      "coordinates": {"latitude": 38.9438, "longitude": -92.3268},
      "category": "dorm"
    },
    ...
  ]
}
```

**Routes Response (Normal):**
```json
{
  "response_type": "routes",
  "routes": [...],
  "explanation": "I've found 3 routes..."
}
```

---

## Conversation Flow Examples

### Example 1: Disambiguation Flow

```
User: "Take me to a dorm"

Agent: "I found several dorms on campus. Which one would you like to go to?
1. Hatch Hall
2. Mark Twain Hall
3. College Avenue Hall
..."

User: "Hatch Hall"

Agent: "Great! How would you like to travel to Hatch Hall?
🚶 Walk | 🚴 Bike | 🚗 Drive | 🚌 Bus"

User: "Walk"

Agent: "I've found 3 safe routes to Hatch Hall..."
```

### Example 2: Direct Location with Mode

```
User: "Bike to Ellis Library"

Agent: "I've found 3 bike routes to Ellis Library. The safest route takes 8 minutes..."
```

### Example 3: Category with Mode in Same Message

```
User: "Drive to a parking garage"

Agent: "I found several parking locations. Which would you like?
1. Parking Garage A
2. Parking Garage B
..."
```

---

## Tool Configuration

### Tools Available to Agent

Ensure these tools are configured:

1. **get_safe_route**
   - Updated to accept `transportation_mode` parameter
   - Values: "foot", "bike", "car", "bus"

2. **get_location_options** (NEW)
   - Parameters: `category` (string)
   - Returns: List of location options
   - Called automatically by backend when category detected

3. **geocode_location**
   - Existing tool, no changes needed

---

## Testing Your Configuration

### Test Queries

Use these queries to verify the configuration:

**Disambiguation Tests:**
```
1. "Take me to a dorm"
   → Should ask which dorm

2. "Find me food"
   → Should ask which dining hall

3. "Where's a library"
   → Should ask which library (or go directly if only one)
```

**Transportation Mode Tests:**
```
1. "Bike to Ellis Library"
   → Should use bike routing

2. "I want to drive to the rec center"
   → Should use car routing

3. "Can I take the bus?"
   → Should use bus/walking combination
```

**Combined Tests:**
```
1. "Bike to a dorm"
   → Should ask which dorm, then use bike routing

2. "Drive to food"
   → Should ask which dining hall, then use car routing
```

---

## Troubleshooting

### Issue: Agent doesn't recognize categories

**Solution**: Add more category keywords to training data
- Dorm: Also try "residence", "housing"
- Dining: Also try "cafeteria", "restaurant", "cafe"
- Library: Usually well-recognized

### Issue: Mode extraction fails

**Solution**: Ensure keywords are in agent's training:
- "bike" → mode: bike
- "drive" / "car" → mode: car
- "bus" / "shuttle" → mode: bus

### Issue: Disambiguation response not displayed properly

**Solution**: Check response_type handling in agent prompt
- Agent should check for `response_type: "disambiguation"`
- Format location list clearly for user selection

---

## Configuration Checklist

- [ ] Updated agent system prompt with disambiguation capabilities
- [ ] Added category keywords to training data
- [ ] Added transportation mode keywords to training data
- [ ] Configured response_type handling
- [ ] Tested disambiguation flow with "Take me to a dorm"
- [ ] Tested transportation modes (walk/bike/drive/bus)
- [ ] Tested combined queries ("Bike to a dorm")
- [ ] Verified fallback behavior (single location skips disambiguation)

---

## Next Steps After Configuration

1. Test the agent in Archia console with sample queries
2. Integrate with frontend chat UI
3. Monitor conversation logs for edge cases
4. Refine category keywords based on user patterns
5. Add more specific location names to agent knowledge base
