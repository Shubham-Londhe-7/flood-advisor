# 🌊 Pune Flood Advisor

A real-time waterlogging risk map for Pune, built to help commuters avoid flood-prone roads during monsoon season.

**Live demo:** _(add your deployed link here once live)_

## Problem

Every monsoon, certain roads and underpasses in Pune (Sinhagad Road, Karve Road Underpass, Bibwewadi Underpass, and more) flood repeatedly — causing traffic jams, vehicle damage, and safety risks. There's no easy, live way to check which roads are currently risky before heading out.

## What it does

- Displays known flood-prone zones across Pune on an interactive map, color-coded by risk level (low/medium/high)
- Lets users submit live waterlogging reports with one tap — reports feed back into the risk score in real time
- Risk score combines historical flood-frequency data with live crowd-sourced reports
- Auto-refreshes every minute during active use

## Tech stack

**Backend:** FastAPI, SQLAlchemy, PostgreSQL (Supabase)
**Frontend:** React, Leaflet / react-leaflet
**Deployment:** Render (API), Vercel (frontend)

## Architecture

```
React + Leaflet (frontend)
        │
        ▼
   FastAPI backend  ──────►  PostgreSQL (Supabase)
   - GET /zones               - flood_zones table
   - POST /report             - reports table
   - GET /reports
```

Risk score for each zone = historical baseline risk + weighted boost from nearby live reports.

## Running locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
# create .env with DATABASE_URL=<your postgres connection string>
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/zones` | List all flood zones with current risk score |
| POST | `/report` | Submit a live waterlogging report (lat, lon, severity) |
| GET | `/reports` | List all submitted reports |

## Roadmap

- [ ] Integrate live rainfall data (OpenWeatherMap/IMD) into risk scoring
- [ ] Route-check API — warn users if a planned route crosses a high-risk zone
- [ ] Historical backtesting — validate risk model against past flood events
- [ ] Expand seeded zone list beyond initial 5 spots

## Why this project

Built to solve a real, recurring civic problem in Pune using tools I already know (FastAPI, React, PostgreSQL) — deployed as a working system, not just a local demo.