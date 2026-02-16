# Campus Dispatch Copilot - Interactive Map Design Specification

**Version:** 1.0  
**Date:** February 2026  
**Component:** Map Panel  
**Library:** Leaflet.js 1.9.4 with React-Leaflet 4.2.1

---

## Table of Contents

1. [Map Overview](#map-overview)
2. [Visual Appearance](#visual-appearance)
3. [Map Layers](#map-layers)
4. [Route Visualization](#route-visualization)
5. [Markers & Icons](#markers--icons)
6. [Interactive Elements](#interactive-elements)
7. [Map Controls](#map-controls)
8. [Legend System](#legend-system)
9. [Overlays & Banners](#overlays--banners)
10. [Popups & Tooltips](#popups--tooltips)
11. [Responsive Behavior](#responsive-behavior)
12. [State Management](#state-management)
13. [User Interactions](#user-interactions)
14. [Performance Optimizations](#performance-optimizations)
15. [Implementation Examples](#implementation-examples)

---

## Map Overview

### Purpose

The map is the **visual centerpiece** of the Campus Dispatch Copilot, serving as:
- Primary navigation interface for route visualization
- Safety data display system (incidents, emergency phones, patrol zones)
- Real-time contextual information provider (time of day, weather, conditions)
- Decision-making tool (compare multiple routes visually)

### Design Philosophy

**Safety-Centric Cartography**
- Route safety levels must be instantly recognizable
- Incident locations should be obvious but not alarming
- Emergency resources (phones, police) should be highlighted as positive elements
- Clean, minimal base map lets safety data stand out

**Information Hierarchy**
1. **Primary**: Route paths (thick, colorful, animated)
2. **Secondary**: Incidents and emergency phones (markers)
3. **Tertiary**: Base map streets and buildings (muted)
4. **Ambient**: Legend, controls, banners (accessible but not distracting)

### Viewport Specifications

**Desktop (≥1024px)**
- Container: Right panel, flexible width (typically 60% of screen)
- Height: `calc(100vh - 60px)` (full height minus header)
- Minimum width: 600px
- Recommended: 800-1200px

**Tablet (768-1023px)**
- Container: Right panel, 55% of screen
- Height: `calc(100vh - 60px)`
- Minimum width: 400px

**Mobile (≤767px)**
- Container: Full screen when Map tab is active
- Height: `calc(100vh - 110px)` (minus header and bottom nav)
- Width: 100vw
- Touch-optimized controls

---

## Visual Appearance

### Base Map Style

**Light Mode (Default)**

**Map Tiles**: CartoDB Positron (Clean, minimal, professional)
```
Tile URL: https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png
Attribution: © OpenStreetMap contributors © CARTO
```

**Visual Characteristics:**
- Background: Very light gray (#F5F5F5)
- Roads: White with light gray borders
- Major roads: Slightly darker gray (#E0E0E0)
- Water bodies: Very light blue (#E8F4F8)
- Parks/green spaces: Very light green (#F0F8F0)
- Buildings: Light gray outlines (#DEDEDE)
- Text labels: Dark gray (#666666), subtle

**Why CartoDB Positron:**
- Extremely clean and minimal (doesn't compete with route overlays)
- Excellent readability
- Low visual noise
- Professional appearance
- Free to use with attribution

---

**Dark Mode**

**Map Tiles**: CartoDB Dark Matter
```
Tile URL: https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png
Attribution: © OpenStreetMap contributors © CARTO
```

**Visual Characteristics:**
- Background: Very dark blue-gray (#1A1A1A)
- Roads: Dark gray (#2A2A2A) with darker borders
- Major roads: Lighter gray (#3A3A3A)
- Water bodies: Dark blue (#1A2A3A)
- Parks: Dark green (#1A2A1A)
- Buildings: Subtle dark outlines (#252525)
- Text labels: Light gray (#AAAAAA)

**Dark Mode Benefits:**
- Reduces eye strain at night
- Better for OLED screens (battery saving)
- Doesn't destroy night vision for walking students
- Makes safety markers pop even more

---

**Alternative Map Styles (Advanced Option)**

Users can optionally switch map styles via settings:

**Option 2: OpenStreetMap Standard**
```
Tile URL: https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```
- More detailed street labels
- Traditional map appearance
- Familiar to users of Google Maps

**Option 3: Satellite Hybrid** (Future Enhancement)
```
Tile URL: Mix of satellite imagery with street labels
```
- Aerial photography base
- Street names overlaid
- Helps identify actual campus locations
- More visually engaging but potentially distracting

---

### Map Bounds & Zoom

**Initial View**

**Center Point**: University of Missouri campus center
- Latitude: 38.9404
- Longitude: -92.3277

**Default Zoom Level**: 16
- Shows ~1 mile radius
- Entire main campus visible
- Buildings identifiable
- Good balance of detail and overview

**Zoom Constraints**
- Minimum Zoom: 14 (prevent zooming out too far - keep focus on campus)
- Maximum Zoom: 19 (prevent zooming in too close - tile quality degrades)

**Campus Boundary Restriction** (Optional but recommended)
- Define maximum bounds to prevent panning off campus
- Bounds: 
  - North: 39.0000
  - South: 38.8800
  - East: -92.2500
  - West: -92.4000

---

### Map Container Styling

**CSS Properties**
```css
.map-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: #f5f5f5;  /* Matches light tile background */
  overflow: hidden;
}

[data-theme="dark"] .map-container {
  background: #1a1a1a;  /* Matches dark tile background */
}

.leaflet-container {
  width: 100%;
  height: 100%;
  font-family: 'Inter', -apple-system, sans-serif;
  z-index: 0;  /* Base layer */
}

/* Smooth transitions during pan/zoom */
.leaflet-zoom-animated {
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## Map Layers

### Layer Structure (Bottom to Top)

```
┌─────────────────────────────────────┐
│ Layer 7: Popups & Tooltips         │ (z-index: 700)
├─────────────────────────────────────┤
│ Layer 6: Controls & UI Elements    │ (z-index: 600)
├─────────────────────────────────────┤
│ Layer 5: Conditions Banner         │ (z-index: 500)
├─────────────────────────────────────┤
│ Layer 4: Markers (Phones, Incidents)│ (z-index: 400)
├─────────────────────────────────────┤
│ Layer 3: Route Polylines           │ (z-index: 300)
├─────────────────────────────────────┤
│ Layer 2: Patrol Zones (Optional)   │ (z-index: 200)
├─────────────────────────────────────┤
│ Layer 1: Base Map Tiles            │ (z-index: 0)
└─────────────────────────────────────┘
```

### Layer 1: Base Map Tiles

**Configuration**
```javascript
const baseMapOptions = {
  attribution: '© OpenStreetMap contributors © CARTO',
  maxZoom: 19,
  minZoom: 14,
  tileSize: 256,
  zoomOffset: 0,
  detectRetina: true,  // High-DPI screen support
  crossOrigin: true,
  updateWhenIdle: false,  // Smooth updates
  keepBuffer: 2,  // Cache 2 tile layers around viewport
};
```

### Layer 2: Patrol Zones (Optional Heatmap)

**Purpose**: Show areas with high police patrol frequency

**Visual Style**
- Semi-transparent overlays
- Color: Blue tint (#2563eb with 10% opacity)
- No borders (soft edges)
- Blends into map

**Data Structure**
```javascript
const patrolZone = {
  type: 'Feature',
  geometry: {
    type: 'Polygon',
    coordinates: [/* array of lat/lng points */]
  },
  properties: {
    patrol_frequency: 'high',  // 'high', 'moderate', 'low'
    zone_name: 'Main Campus Quad'
  }
};
```

**Styling**
```javascript
const patrolZoneStyle = {
  fillColor: '#2563eb',
  fillOpacity: 0.10,
  stroke: false,
  interactive: false  // Don't block clicks on routes/markers
};
```

**Toggle**: Users can show/hide via layer control

---

### Layer 3: Route Polylines

**Purpose**: Show walking paths between origin and destination

**Visual Properties**

**Polyline Specifications**
- Width: 6px (desktop), 8px (mobile)
- Opacity: 0.85 (non-selected), 1.0 (selected)
- Cap style: Round
- Join style: Round
- Smoothing: Enabled (smoothFactor: 1.5)

**Color Coding by Safety Level**
```javascript
const routeColors = {
  'very-safe':   '#10b981',  // Green (0-20 risk)
  'safe':        '#84cc16',  // Light green (21-40 risk)
  'moderate':    '#f59e0b',  // Amber (41-60 risk)
  'caution':     '#f97316',  // Orange (61-80 risk)
  'warning':     '#ef4444'   // Red (81-100 risk)
};
```

**Selection States**
```javascript
// Non-selected route
const defaultRouteStyle = {
  color: routeColors[riskLevel],
  weight: 6,
  opacity: 0.85,
  smoothFactor: 1.5,
  lineCap: 'round',
  lineJoin: 'round'
};

// Selected/active route
const selectedRouteStyle = {
  color: routeColors[riskLevel],
  weight: 8,
  opacity: 1.0,
  smoothFactor: 1.5,
  lineCap: 'round',
  lineJoin: 'round',
  className: 'route-polyline--selected'  // For CSS glow effect
};

// Hover state (if not selected)
const hoverRouteStyle = {
  weight: 7,
  opacity: 0.95
};
```

**Glow Effect (Selected Route)**
```css
.route-polyline--selected {
  filter: drop-shadow(0 0 8px currentColor);
}
```

**Visual Hierarchy**
- Recommended route: Slightly thicker, brighter
- Alternative routes: Standard thickness, slightly faded
- When one route selected: Others fade to 50% opacity

---

### Layer 4: Markers

**Purpose**: Show point locations (incidents, emergency phones, user position)

**Marker Types**

#### A. Incident Markers

**Visual Design**
```
┌─────────────┐
│   ⚠️ or 🚨   │  32px diameter circle
│   Red bg    │  White border (3px)
└─────────────┘
```

**Specifications**
- Size: 32px × 32px (desktop), 36px × 36px (mobile)
- Background: `#ef4444` (safety-warning red)
- Border: 3px solid white (ensures visibility on any map)
- Icon: Unicode warning symbol ⚠️ or siren 🚨
- Shadow: `0 2px 8px rgba(239, 68, 68, 0.4)`
- Animation: Gentle pulse (2s infinite loop)

**Clustering**
When many incidents are close together:
- Cluster into numbered bubble
- Shows count: "5 incidents"
- Clicking expands to individual markers
- Cluster color intensity based on incident severity

```javascript
const incidentMarkerOptions = {
  iconSize: [32, 32],
  iconAnchor: [16, 16],  // Center of icon
  popupAnchor: [0, -20], // Above icon
  className: 'marker-incident',
  html: '<div class="marker-content">🚨</div>'
};
```

---

#### B. Emergency Phone Markers

**Visual Design**
```
┌─────────────┐
│   📞        │  32px diameter circle
│   Blue bg   │  White border (2px)
└─────────────┘
```

**Specifications**
- Size: 32px × 32px (desktop), 36px × 36px (mobile)
- Background: `#2563eb` (primary blue)
- Border: 2px solid white
- Icon: Unicode phone 📞 or custom phone SVG
- Shadow: `0 2px 4px rgba(37, 99, 235, 0.3)`
- Subtle glow: Green outline (indicates safety resource)

**Differentiation from Incidents**
- Cooler color (blue vs red)
- No animation (static, calm presence)
- Slightly different size (helps distinguish at a glance)

```javascript
const phoneMarkerOptions = {
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -20],
  className: 'marker-phone',
  html: '<div class="marker-content">📞</div>'
};
```

---

#### C. User Location Marker

**Visual Design**
```
┌─────────────┐
│   You Are   │  Pulsing blue dot
│   Here      │  with accuracy circle
└─────────────┘
```

**Specifications**
- Size: 16px × 16px blue dot
- Outer ring: 24px pulsing animation
- Accuracy circle: Semi-transparent blue based on GPS accuracy
- Shadow: Subtle drop shadow
- Label: "You" appears on hover

**States**
- **Acquiring GPS**: Gray spinner
- **GPS Locked**: Blue dot with pulse
- **GPS Lost**: Gray dot with question mark

```javascript
const userLocationOptions = {
  radius: 8,
  fillColor: '#2563eb',
  fillOpacity: 1,
  stroke: true,
  color: 'white',
  weight: 3,
  className: 'marker-user-location'
};
```

**Accuracy Circle**
```javascript
const accuracyCircleOptions = {
  radius: gpsAccuracyInMeters,
  fillColor: '#2563eb',
  fillOpacity: 0.15,
  stroke: true,
  color: '#2563eb',
  weight: 2,
  opacity: 0.5
};
```

---

#### D. Origin & Destination Markers

**Origin (Start Point)**
```
┌─────────────┐
│   🏁 START  │  Green flag
│   Green bg  │  
└─────────────┘
```

**Destination (End Point)**
```
┌─────────────┐
│   📍 END    │  Red pin
│   Red bg    │  
└─────────────┘
```

**Specifications**
- Size: 40px × 40px (slightly larger than other markers)
- Origin: Green background, flag emoji or checkered flag
- Destination: Red background, location pin emoji
- Both have labels that appear on map (not just in popup)
- Always visible (don't cluster these)

---

### Marker Clustering

**When to Cluster**
- More than 10 markers visible in current viewport
- Markers within 40px of each other (at current zoom)
- Only cluster incidents (not emergency phones, user location, or route endpoints)

**Cluster Appearance**
```
┌──────────────┐
│     12       │  40px diameter
│  incidents   │  Red gradient
└──────────────┘
```

**Properties**
- Background: Gradient from light red to dark red (based on count)
- Text: White, bold, number of markers
- Size: Scales with count (40px for 2-10, 50px for 11-50, 60px for 51+)
- Click: Zooms in to show individual markers (spider-legs if needed)

```javascript
const clusterOptions = {
  maxClusterRadius: 40,
  spiderfyOnMaxZoom: true,
  showCoverageOnHover: false,
  zoomToBoundsOnClick: true,
  iconCreateFunction: (cluster) => {
    const count = cluster.getChildCount();
    const size = count < 10 ? 40 : count < 50 ? 50 : 60;
    return L.divIcon({
      html: `<div class="marker-cluster">${count}</div>`,
      className: 'marker-cluster-wrapper',
      iconSize: [size, size]
    });
  }
};
```

---

## Route Visualization

### Route Drawing Animation

**Initial Appearance**
When routes are first loaded, they should draw progressively:

**Animation Sequence**
1. Route path appears as a thin line from origin (0.3s)
2. Line thickens to full width (0.2s)
3. Color fills in from start to end (0.5s)
4. Total animation: ~1 second per route
5. Routes draw simultaneously, not sequentially

**Implementation**
```javascript
// Using SVG stroke-dasharray animation
const routePath = L.polyline(coordinates, {
  color: routeColor,
  weight: 6,
  className: 'route-animated'
});

// CSS animation
.route-animated {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: routeDraw 1s ease-out forwards;
}

@keyframes routeDraw {
  to {
    stroke-dashoffset: 0;
  }
}
```

---

### Route Selection States

**State 1: All Routes Visible (Initial)**
- All routes displayed at full opacity (0.85)
- Equal visual weight (same thickness)
- Colors indicate safety level
- User can compare visually

**State 2: Route Hovered**
- Hovered route: Weight increases to 7px, opacity 0.95
- Other routes: No change
- Cursor changes to pointer
- Tooltip appears showing route name and risk score

**State 3: Route Selected**
- Selected route: Weight 8px, opacity 1.0, glowing effect
- Other routes: Fade to 50% opacity, weight 5px
- Map pans/zooms to fit selected route bounds
- Corresponding route card in chat panel highlights

**State 4: Route Comparison Mode** (Advanced)
- Two routes selected simultaneously
- Both at full opacity with glow
- Others completely hidden
- Side-by-side comparison enabled

---

### Waypoints & Turn Indicators

**Route Waypoints** (Optional Enhancement)
- Small circles along route at major turns
- Size: 8px diameter
- Color: Same as route color but slightly darker
- Shows complexity of route (more turns = more waypoints)

**Turn-by-Turn Arrows** (Future Enhancement)
- Directional arrows along route
- Appear every 100-200 meters
- Point in direction of travel
- Help visualize the path direction

---

### Route Distance Markers

**Distance Labels on Route**
- Every 0.25 miles (400 meters)
- Small text label showing cumulative distance
- Background: Semi-transparent white pill
- Font: 10px, medium weight
- Example: "0.3 mi" or "500m"

**Styling**
```css
.route-distance-marker {
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 500;
  color: #0f172a;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}
```

---

## Interactive Elements

### Click/Tap Interactions

**Map Background**
- **Click empty space**: Deselect current route, return to overview
- **Double-click**: Zoom in one level
- **Right-click**: Context menu (future enhancement)

**Routes**
- **Click route**: Select route, highlight, show details
- **Hover route**: Temporary highlight, show tooltip
- **Click selected route again**: Deselect

**Markers**
- **Click marker**: Open popup with details
- **Hover marker**: Show tooltip (brief info)
- **Click cluster**: Zoom in or spiderfy

**Legend**
- **Click legend item**: Toggle visibility of that layer
- **Click legend header**: Collapse/expand legend

**Controls**
- **Click zoom buttons**: Zoom in/out
- **Click locate button**: Center on user location
- **Click fullscreen**: Toggle fullscreen mode

---

### Hover States

**Route Hover**
```
┌─────────────────────────────────────────┐
│ Conley Avenue Route                     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Risk Score: 15/100 - Very Safe          │
│ Duration: 8 minutes                     │
└─────────────────────────────────────────┘
```

**Marker Hover**
```
┌─────────────────────────┐
│ Emergency Phone         │
│ Direct line to police   │
└─────────────────────────┘
```

**Control Hover**
- Slight scale increase (1.05)
- Background color change (lighter/darker)
- Cursor: pointer
- Tooltip with control name

---

### Drag & Pan

**Pan Behavior**
- Click and drag to move map
- Inertia enabled (map continues briefly after release)
- Smooth deceleration
- Double-click to recenter on selected route

**Pan Limits**
- Constrained to campus bounds (optional)
- Prevents panning too far off-campus
- If user tries to pan beyond, gentle bounce-back animation

---

### Zoom Interactions

**Zoom Methods**
1. **Zoom Buttons**: +/- controls in top-right
2. **Mouse Wheel**: Scroll up/down to zoom
3. **Pinch Gesture**: Two-finger pinch on mobile
4. **Double-Click**: Zoom in one level centered on click point
5. **Shift + Drag**: Box zoom (draw rectangle to zoom to that area)

**Zoom Animation**
- Smooth transition (300ms ease-out)
- Center point remains stable
- Markers fade in/out gracefully during zoom

**Zoom-Dependent Visibility**
- Zoom 14-15: Show only route, major landmarks
- Zoom 16-17: Show incidents, emergency phones
- Zoom 18-19: Show all details, building labels, parking

---

## Map Controls

### Control Panel Layout

**Desktop Position**
```
Map Top-Right Corner:
┌─────────────────┐
│ [ + ]  Zoom In  │
│ [ - ]  Zoom Out │
│ [ ⊙ ]  Locate   │
│ [ ⛶ ]  Fullscreen│
│ [ ≡ ]  Layers   │
└─────────────────┘
```

**Mobile Position**
```
Map Top-Right Corner (larger buttons):
┌──────────────────┐
│ [ + ]  48×48px   │
│ [ - ]            │
│ [ ⊙ ]            │
│ [ ⛶ ]            │
└──────────────────┘
```

---

### 1. Zoom Controls

**Zoom In Button (+)**
```css
.leaflet-control-zoom-in {
  width: 40px;
  height: 40px;
  border-radius: 8px 8px 0 0;
  background: white;
  border: 2px solid #e2e8f0;
  font-size: 20px;
  font-weight: 600;
  color: #0f172a;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.leaflet-control-zoom-in:hover {
  background: #f1f5f9;
  border-color: #2563eb;
  color: #2563eb;
}

@media (max-width: 767px) {
  .leaflet-control-zoom-in {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }
}
```

**Zoom Out Button (-)**
- Same styling as Zoom In
- Border-radius: `0 0 8px 8px`
- 1px border-top (separates from + button)

**Behavior**
- Click: Zoom in/out one level
- Hold: Continuous zoom (not implemented by default, but possible)
- Disabled state when at min/max zoom (opacity 0.5, cursor not-allowed)

---

### 2. Locate Me Control

**Current Location Button**
```
┌─────────┐
│   ⊙     │  Crosshair icon
│  Locate │  or GPS icon
└─────────┘
```

**States**

**Idle State**
- Icon: Gray crosshair ⊙
- Background: White
- Tooltip: "Show my location"

**Loading State**
- Icon: Spinning GPS icon
- Background: Light blue
- Tooltip: "Acquiring GPS..."
- Animation: Rotate 360° every 1s

**Active State**
- Icon: Blue filled circle
- Background: Light blue
- Tooltip: "Location found"
- Map centered on user

**Error State**
- Icon: Red crosshair with X
- Background: Light red
- Tooltip: "Location unavailable"
- Shows error message in popup

**Functionality**
```javascript
const locateUser = () => {
  map.locate({
    setView: true,        // Center on user
    maxZoom: 17,          // Don't zoom too close
    enableHighAccuracy: true,
    timeout: 10000,       // 10s timeout
    watch: true          // Continue tracking
  });
};

map.on('locationfound', (e) => {
  // Show user marker at e.latlng
  // Show accuracy circle with radius e.accuracy
  // Center map on user
});

map.on('locationerror', (e) => {
  // Show error toast
  // Reset locate button to idle state
});
```

---

### 3. Fullscreen Control

**Fullscreen Toggle**
```
┌───────────┐
│   ⛶       │  Expand icon
│ Fullscreen│  
└───────────┘
```

**Behavior**
- Click: Toggle fullscreen mode
- Fullscreen ON: Icon changes to compress ⛶
- Fullscreen OFF: Icon shows expand ⛶
- ESC key exits fullscreen

**Fullscreen Effects**
- Map expands to fill entire viewport
- All other UI elements hidden (except map controls)
- Higher z-index (9999)
- Exit button always visible

---

### 4. Layer Control

**Layer Panel Toggle**
```
┌───────────┐
│   ≡       │  Hamburger menu
│  Layers   │  
└───────────┘
```

**Expanded Layer Panel**
```
┌──────────────────────────┐
│ MAP LAYERS               │
│ ━━━━━━━━━━━━━━━━━━━━━━ │
│ Base Maps                │
│ ○ Light (default)        │
│ ○ Dark                   │
│ ○ Satellite              │
│                          │
│ Overlays                 │
│ ☑ Routes                 │
│ ☑ Incidents              │
│ ☑ Emergency Phones       │
│ ☑ Patrol Zones           │
│ ☑ User Location          │
└──────────────────────────┘
```

**Toggle Behavior**
- Click layer name: Toggle visibility
- Only one base map active at a time (radio buttons)
- Multiple overlays can be active (checkboxes)
- Changes take effect immediately
- State persists in localStorage

---

### 5. Refresh Data Button (Custom)

**Refresh Control**
```
┌───────────┐
│   ↻       │  Circular arrow
│  Refresh  │  
└───────────┘
```

**Behavior**
- Click: Reload incidents, phones, patrol data
- Loading state: Icon spins during fetch
- Success: Green checkmark appears briefly
- Error: Red X appears briefly
- Throttled: Can't refresh more than once per 30 seconds

**Visual Feedback**
```javascript
const refreshData = async () => {
  // Show loading state
  setRefreshLoading(true);
  
  try {
    await fetchLatestData();
    // Show success
    showToast('Data updated', 'success');
  } catch (error) {
    // Show error
    showToast('Update failed', 'error');
  } finally {
    setRefreshLoading(false);
  }
};
```

---

### 6. Time Simulator (Demo Feature)

**Simulate Day/Night Toggle**
```
┌─────────────────┐
│ ☀️ Simulate     │
│    Night        │
└─────────────────┘
```

**Purpose**
- Shows how route risk scores change based on time of day
- Useful for demo and user education
- Toggles between daytime (2 PM) and nighttime (11 PM) views

**Effects When Activated**
- Conditions banner changes (sun → moon icon)
- Map tiles switch to dark mode
- Risk scores recalculate with night multiplier
- Route colors may shift (same route becomes more yellow/orange)

---

## Legend System

### Legend Position & Appearance

**Desktop**
```
Bottom-Left Corner:
┌─────────────────────────────┐
│ 🗺️  SAFETY LEGEND          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Routes                      │
│ ▬▬▬ Very Safe (0-20)       │
│ ▬▬▬ Safe (21-40)           │
│ ▬▬▬ Moderate (41-60)       │
│ ▬▬▬ Caution (61-80)        │
│ ▬▬▬ Warning (81-100)       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Markers                     │
│ 🚨 Recent Incident          │
│ 📞 Emergency Phone          │
│ 👮 High Patrol Area         │
└─────────────────────────────┘
```

**Mobile**
- Collapsed by default (just icon visible)
- Tap icon to expand
- Floats in bottom-left
- Semi-transparent background

---

### Legend Structure

**Container**
```css
.map-legend {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 600;
  max-width: 250px;
  transition: all 0.3s ease;
}

[data-theme="dark"] .map-legend {
  background: rgba(15, 23, 42, 0.95);
  color: #f1f5f9;
}

/* Collapsed state (mobile) */
.map-legend--collapsed {
  width: 48px;
  height: 48px;
  padding: 12px;
  border-radius: 50%;
}
```

**Legend Title**
```css
.map-legend__title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}
```

**Legend Items**
```css
.map-legend__item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.map-legend__color {
  width: 24px;
  height: 4px;
  border-radius: 2px;
  flex-shrink: 0;
}

.map-legend__icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}
```

---

### Interactive Legend

**Clickable Items**
- Click route color: Highlight all routes of that safety level
- Click marker icon: Toggle visibility of that marker type
- Click section header: Collapse/expand that section

**Visual States**
- Active (visible): Full opacity, checkmark icon
- Inactive (hidden): 50% opacity, X icon
- Hover: Slight scale increase, background highlight

---

## Overlays & Banners

### Conditions Banner

**Purpose**: Show current time-of-day context and how it affects risk

**Position**: Top center of map (floating)

**Daytime Appearance**
```
┌──────────────────────────────────────┐
│ ☀️  DAYTIME CONDITIONS (2:15 PM)    │
│ Risk levels are lower during daylight│
└──────────────────────────────────────┘
```

**Styling**
```css
.conditions-banner {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(37, 99, 235, 0.95);
  backdrop-filter: blur(10px);
  color: white;
  padding: 12px 24px;
  border-radius: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 500;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}

@media (max-width: 767px) {
  .conditions-banner {
    font-size: 12px;
    padding: 10px 16px;
  }
}
```

**Nighttime Appearance**
```
┌─────────────────────────────────────────┐
│ 🌙  NIGHTTIME CONDITIONS (11:23 PM)    │
│ ⚠️  Higher risk - safety prioritized   │
└─────────────────────────────────────────┘
```

**Nighttime Styling**
```css
.conditions-banner--night {
  background: rgba(88, 28, 135, 0.95);  /* Purple gradient */
  animation: gentlePulse 3s ease-in-out infinite;
}

@keyframes gentlePulse {
  0%, 100% { opacity: 0.95; }
  50% { opacity: 1; }
}
```

---

### Route Info Overlay (When Route Selected)

**Position**: Top-left corner (below conditions banner)

**Appearance**
```
┌────────────────────────────────────┐
│ SELECTED ROUTE                     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Via Conley Avenue                  │
│ 🟢 Risk: 15/100                    │
│ ⏱️  8 minutes · 📏 850 meters      │
│                                    │
│ [View Details →]                   │
└────────────────────────────────────┘
```

**Purpose**
- Quick reference when looking at map
- Complements route card in chat panel
- Always visible without scrolling chat

---

### Loading Overlay

**When Fetching New Data**
```
┌──────────────────────────────────┐
│                                  │
│    [Spinner animation]           │
│                                  │
│    Loading safety data...        │
│                                  │
└──────────────────────────────────┘
```

**Styling**
```css
.map-loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  z-index: 800;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

[data-theme="dark"] .map-loading-overlay {
  background: rgba(15, 23, 42, 0.9);
}
```

---

## Popups & Tooltips

### Marker Popups

**Incident Popup**
```
┌───────────────────────────────────┐
│ ⚠️  Theft Incident                │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Date: January 10, 2024            │
│ Time: 11:45 PM                    │
│ Location: Parking Lot B           │
│                                   │
│ Description:                      │
│ Bike theft reported near          │
│ the north entrance                │
│                                   │
│ [View Report] [Close ✕]          │
└───────────────────────────────────┘
```

**Styling**
```css
.leaflet-popup-content-wrapper {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 250px;
  max-width: 350px;
}

[data-theme="dark"] .leaflet-popup-content-wrapper {
  background: #1e293b;
  color: #f1f5f9;
}

.leaflet-popup-content {
  margin: 0;
  line-height: 1.6;
}

.popup-header {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.popup-divider {
  height: 1px;
  background: var(--color-border-light);
  margin: 12px 0;
}

.popup-field {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 13px;
}

.popup-field__label {
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 70px;
}

.popup-field__value {
  color: var(--color-text-primary);
}
```

---

**Emergency Phone Popup**
```
┌───────────────────────────────────┐
│ 📞  Emergency Call Box            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Direct line to Campus Police      │
│                                   │
│ Available: 24/7                   │
│ Response Time: < 5 minutes        │
│                                   │
│ Location: Outside Memorial Union  │
│                                   │
│ [Get Directions] [Close ✕]       │
└───────────────────────────────────┘
```

**Visual Cues**
- Green accent border (indicates safety resource)
- Phone icon in header
- "Available 24/7" in green text
- Reassuring tone

---

### Tooltips (Hover)

**Route Tooltip**
```
┌─────────────────────────────┐
│ Conley Avenue Route         │
│ Risk: 15/100 · 8 min        │
└─────────────────────────────┘
```

**Marker Tooltip**
```
┌──────────────────┐
│ Theft - Jan 10   │
└──────────────────┘
```

**Control Tooltip**
```
┌───────────────────┐
│ Zoom In (Ctrl +)  │
└───────────────────┘
```

**Styling**
```css
.leaflet-tooltip {
  background: rgba(15, 23, 42, 0.95);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
}

.leaflet-tooltip-top:before {
  border-top-color: rgba(15, 23, 42, 0.95);
}
```

---

## Responsive Behavior

### Desktop (≥1024px)

**Map Container**
- Width: Flexible (60% of viewport typically)
- Height: `calc(100vh - 60px)`
- Controls: Standard size (40px buttons)
- Legend: Always expanded
- Tooltips: Appear on hover

**Optimal Viewing**
- Zoom level: 16 (default)
- 3-5 routes visible simultaneously
- All markers visible
- Legend readable without zooming

---

### Tablet (768-1023px)

**Map Container**
- Width: 55% of viewport (in split-screen mode)
- Height: `calc(100vh - 60px)`
- Controls: Slightly larger (44px buttons)
- Legend: Collapsible
- Touch optimizations active

**Adjustments**
- Larger tap targets
- Simplified legend
- Fewer route labels visible

---

### Mobile (≤767px)

**Map Container**
- Width: 100vw (full screen when active)
- Height: `calc(100vh - 110px)` (minus header + bottom nav)
- Controls: Large (48px buttons)
- Legend: Collapsed by default (tap to expand)
- Touch-first interactions

**Mobile-Specific Changes**

**Simplified Legend**
```
Collapsed:
┌─────┐
│  🗺  │
└─────┘

Expanded (tap to open):
┌──────────────────┐
│ Routes           │
│ ▬▬ Very Safe     │
│ ▬▬ Moderate      │
│ ▬▬ Warning       │
│                  │
│ 🚨 Incidents     │
│ 📞 Phones        │
└──────────────────┘
```

**Touch Gestures**
- Single tap: Select route/marker
- Double tap: Zoom in
- Pinch: Zoom in/out
- Two-finger drag: Pan map
- Long press: Show context menu (future)

**Route Selection**
- Tap route polyline: Select route
- Tap again: Deselect
- Tap route card in chat: Switch to map tab and highlight route

**Performance Optimizations**
- Reduce marker detail at lower zooms
- Aggressive clustering (cluster at zoom 15+)
- Lazy load tiles
- Disable hover effects (rely on taps)

---

## State Management

### Map State Object

```typescript
interface MapState {
  // View state
  center: LatLng;
  zoom: number;
  bounds: LatLngBounds;
  
  // Route state
  routes: Route[];
  selectedRouteId: string | null;
  hoveredRouteId: string | null;
  
  // Marker state
  incidents: Incident[];
  emergencyPhones: EmergencyPhone[];
  userLocation: LatLng | null;
  
  // Layer visibility
  layers: {
    routes: boolean;
    incidents: boolean;
    phones: boolean;
    patrolZones: boolean;
    userLocation: boolean;
  };
  
  // UI state
  legendExpanded: boolean;
  fullscreen: boolean;
  loading: boolean;
  
  // Conditions
  timeOfDay: 'day' | 'night';
  simulatedTime: Date | null;
}
```

### State Synchronization

**Map ↔ Chat Sync**

When user selects route in chat:
1. Map receives `selectedRouteId`
2. Map highlights route polyline
3. Map pans/zooms to fit route bounds
4. Other routes fade to 50% opacity

When user clicks route on map:
1. Map emits `routeSelected` event
2. Chat panel scrolls to corresponding route card
3. Route card highlights
4. Details expand

---

## User Interactions

### Interaction Flow Examples

**Flow 1: View Route on Map**
```
User Action          → System Response
─────────────────────────────────────────────
1. Click route card  → Switch to map tab (mobile)
                     → Map pans to route
                     → Route highlighted with glow
                     → Other routes fade
                     
2. Hover route      → Route thickens
                    → Tooltip appears
                    → Cursor changes to pointer
                    
3. Click route      → Route selected
                    → Bounds fit to route
                    → Conditions banner shows
                    → Legend highlights route color
```

**Flow 2: Explore Safety Data**
```
User Action          → System Response
─────────────────────────────────────────────
1. Zoom in          → More incidents appear
                    → Clusters split into individuals
                    → Street names more visible
                    
2. Click incident   → Popup opens
                    → Incident details shown
                    → Related routes dim slightly
                    
3. Click phone      → Popup opens
                    → Phone details shown
                    → "Get Directions" button appears
```

**Flow 3: Compare Routes**
```
User Action          → System Response
─────────────────────────────────────────────
1. View 3 routes    → All routes visible
                    → Colors show safety levels
                    → User can compare visually
                    
2. Click Route A    → Route A highlighted
                    → Other routes fade
                    → Route A details in overlay
                    
3. Shift+Click B    → Comparison mode
                    → Both routes highlighted
                    → Side-by-side stats shown
```

---

## Performance Optimizations

### Tile Loading

**Strategy**
- Preload tiles for current zoom ± 1 level
- Cache tiles in browser (IndexedDB)
- Lazy load tiles outside viewport
- Use lower quality tiles on slow connections

**Configuration**
```javascript
const tileLayerOptions = {
  maxZoom: 19,
  minZoom: 14,
  tileSize: 256,
  zoomOffset: 0,
  updateWhenIdle: false,
  updateWhenZooming: false,
  keepBuffer: 2,  // Keep 2 tile layers cached
  detectRetina: true,
  crossOrigin: true
};
```

---

### Marker Performance

**Clustering**
- Always cluster when more than 50 markers visible
- Use MarkerCluster library with optimizations
- Debounce cluster updates (300ms)

**Virtualization**
- Only render markers in current viewport + buffer
- Remove markers outside viewport
- Re-add when panning back

**Icon Optimization**
- Use SVG icons (smaller, scalable)
- Sprite sheet for multiple markers
- Cache icon instances

---

### Route Rendering

**Simplification**
- Simplify route geometry at lower zooms
- Use Douglas-Peucker algorithm (tolerance: 0.0001)
- Only show full detail at zoom 17+

**Canvas vs SVG**
- Use Canvas renderer for routes (better performance)
- Use SVG for interactive markers (better hit detection)

```javascript
const map = L.map('map', {
  preferCanvas: true,  // Use canvas for paths
  renderer: L.canvas()
});
```

---

### Animation Performance

**Hardware Acceleration**
```css
.route-polyline {
  transform: translateZ(0);  /* Force GPU */
  will-change: opacity, stroke-width;
}

/* Remove will-change after animation */
.route-polyline--animated {
  will-change: auto;
}
```

**Throttle Updates**
- Debounce pan events (50ms)
- Debounce zoom events (100ms)
- Throttle marker updates (200ms)

---

## Implementation Examples

### Complete Map Setup

```typescript
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Map initialization
const map = L.map('map', {
  center: [38.9404, -92.3277],  // MU campus
  zoom: 16,
  minZoom: 14,
  maxZoom: 19,
  preferCanvas: true,
  zoomControl: false  // Add custom controls
});

// Base tile layer
const lightTiles = L.tileLayer(
  'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
  {
    attribution: '© OpenStreetMap contributors © CARTO',
    maxZoom: 19,
    detectRetina: true
  }
);

const darkTiles = L.tileLayer(
  'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
  {
    attribution: '© OpenStreetMap contributors © CARTO',
    maxZoom: 19,
    detectRetina: true
  }
);

// Add default layer
const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
(isDarkMode ? darkTiles : lightTiles).addTo(map);

// Custom zoom control
L.control.zoom({
  position: 'topright',
  zoomInTitle: 'Zoom in',
  zoomOutTitle: 'Zoom out'
}).addTo(map);

// Locate control
L.control.locate({
  position: 'topright',
  strings: {
    title: 'Show my location'
  },
  locateOptions: {
    enableHighAccuracy: true,
    maxZoom: 17
  }
}).addTo(map);
```

---

### Adding Routes

```typescript
const addRouteToMap = (route: Route, isSelected: boolean = false) => {
  const riskLevel = getRiskLevel(route.safety_analysis.risk_score);
  const color = routeColors[riskLevel];
  
  const polyline = L.polyline(route.geometry.coordinates, {
    color: color,
    weight: isSelected ? 8 : 6,
    opacity: isSelected ? 1.0 : 0.85,
    smoothFactor: 1.5,
    lineCap: 'round',
    lineJoin: 'round',
    className: isSelected ? 'route-polyline--selected' : 'route-polyline'
  });
  
  // Add tooltip
  polyline.bindTooltip(
    `${route.name}<br>Risk: ${route.safety_analysis.risk_score}/100 · ${route.duration_minutes} min`,
    {
      sticky: true,
      className: 'route-tooltip'
    }
  );
  
  // Click handler
  polyline.on('click', () => {
    onRouteSelected(route.id);
  });
  
  // Hover handlers
  polyline.on('mouseover', () => {
    if (!isSelected) {
      polyline.setStyle({ weight: 7, opacity: 0.95 });
    }
  });
  
  polyline.on('mouseout', () => {
    if (!isSelected) {
      polyline.setStyle({ weight: 6, opacity: 0.85 });
    }
  });
  
  polyline.addTo(map);
  
  return polyline;
};
```

---

### Adding Markers

```typescript
const addIncidentMarker = (incident: Incident) => {
  const icon = L.divIcon({
    className: 'custom-marker marker-incident',
    html: '<div class="marker-content">🚨</div>',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -20]
  });
  
  const marker = L.marker(
    [incident.location.latitude, incident.location.longitude],
    { icon }
  );
  
  // Popup content
  const popupContent = `
    <div class="incident-popup">
      <div class="popup-header">
        <span>⚠️</span>
        <span>${incident.type}</span>
      </div>
      <div class="popup-divider"></div>
      <div class="popup-field">
        <span class="popup-field__label">Date:</span>
        <span class="popup-field__value">${formatDate(incident.date)}</span>
      </div>
      <div class="popup-field">
        <span class="popup-field__label">Time:</span>
        <span class="popup-field__value">${formatTime(incident.date)}</span>
      </div>
      <div class="popup-field">
        <span class="popup-field__label">Location:</span>
        <span class="popup-field__value">${incident.description}</span>
      </div>
    </div>
  `;
  
  marker.bindPopup(popupContent, {
    maxWidth: 300,
    className: 'custom-popup'
  });
  
  marker.bindTooltip(
    `${incident.type} - ${formatDate(incident.date)}`,
    { className: 'marker-tooltip' }
  );
  
  marker.addTo(map);
  
  return marker;
};
```

---

### Route Animation

```typescript
const animateRouteDraw = (polyline: L.Polyline) => {
  const path = polyline.getElement();
  const length = path.getTotalLength();
  
  path.style.strokeDasharray = `${length}`;
  path.style.strokeDashoffset = `${length}`;
  path.style.animation = 'routeDraw 1s ease-out forwards';
};

// CSS
/*
@keyframes routeDraw {
  to {
    stroke-dashoffset: 0;
  }
}
*/
```

---

## Summary Checklist

### Visual Design ✓
- [x] Clean minimal base map (CartoDB Positron/Dark Matter)
- [x] Route colors match safety levels exactly
- [x] Markers distinctive and recognizable
- [x] Legend clear and accessible
- [x] Dark mode looks professional

### Interactive Features ✓
- [x] Click route to select/highlight
- [x] Click marker to see details
- [x] Zoom controls responsive
- [x] Locate me button works
- [x] Layer toggle functional

### Mobile Experience ✓
- [x] Touch targets ≥48px
- [x] Legend collapsible
- [x] Controls positioned for thumbs
- [x] Gestures work (pinch, double-tap)
- [x] Performance smooth on device

### Accessibility ✓
- [x] All controls keyboard accessible
- [x] ARIA labels on markers
- [x] Tooltips describe elements
- [x] Focus states visible
- [x] Screen reader friendly

### Performance ✓
- [x] Tiles load quickly
- [x] Markers cluster appropriately
- [x] Routes render at 60fps
- [x] No jank during pan/zoom
- [x] Memory doesn't leak

---

This specification provides everything needed to implement a professional, safety-focused, interactive map for the Campus Dispatch Copilot. The map should feel like a powerful tool that empowers students to make informed decisions about their routes. 🗺️