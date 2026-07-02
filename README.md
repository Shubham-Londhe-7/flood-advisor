# Pune Flood/Waterlogging Advisor

Scaffold already here (backend/main.py, frontend/src/FloodMap.jsx).
Use below prompts, one at a time, in Claude Code / Cursor. Review output each step before next.

## Setup
```
cd backend && pip install -r requirements.txt && uvicorn main:app --reload
cd frontend && npm create vite@latest . -- --template react
npm install leaflet react-leaflet
```

## Prompt sequence (feed one at a time, in order)

**Step 1 — get it running**
"Run the FastAPI backend, confirm /zones endpoint returns seeded flood zones. Fix any errors."

**Step 2 — wire frontend**
"Wire FloodMap.jsx into App.jsx as the main view. Confirm map loads centered on Pune, zones show as colored circles."

**Step 3 — test report flow**
"Test the report flow end to end: click map in report mode, submit severity, confirm POST /report succeeds and risk score updates on next fetch."

**Step 4 — swap to real DB**
"Replace in-memory FLOOD_ZONES and REPORTS lists in main.py with Supabase Postgres (use PostGIS extension for geo). Give me the SQL schema first, then update endpoints."

**Step 5 — add live rainfall**
"Add OpenWeatherMap API call in compute_risk() — pull current rainfall intensity for zone's lat/lon, add as weighted factor to risk_score. Cache result 15 min to avoid rate limits."

**Step 6 — route-check feature**
"Add POST /route-check endpoint: takes start {lat,lon} and end {lat,lon}, checks if straight-line path (or OSRM route if available) passes within 500m of any high-risk zone, returns warning + safer alternative if possible."

**Step 7 — deploy**
"Dockerize backend and frontend. Give me docker-compose.yml. Then walk me through deploying backend on Railway/Render and frontend on Vercel."

**Step 8 — polish for resume**
"Add a simple eval script: seed 10 known historical flood events with date+location, backtest risk_score against them, report % where high-risk was correctly flagged before/during event. Print as accuracy metric."

## Notes
- Keep zones list small (15-20) at first — quality over quantity, verify each spot is real (check local news for Pune monsoon flooding reports).
- Step 8 gives you the resume metric: "X% historical flood events correctly flagged as high-risk."
- Don't skip steps — vibe coding tools drift/break things if you ask for everything at once.
