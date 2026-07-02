"""
Pune Flood/Waterlogging Advisor - Backend
Postgres (Supabase) via SQLAlchemy + live rainfall + route-check.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from database import init_db, get_db, FloodZone, Report as ReportModel
from weather import get_rainfall_mm, rainfall_risk_boost
from route_check import check_route

app = FastAPI(title="Pune Flood Advisor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()  # creates tables + seeds zones if empty


class ReportIn(BaseModel):
    lat: float
    lon: float
    severity: int  # 1-5
    note: Optional[str] = None


class RiskScoreResponse(BaseModel):
    zone_id: str
    name: str
    lat: float
    lon: float
    risk_score: float
    risk_level: str
    rainfall_mm: float


class RouteCheckIn(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float


def compute_risk(zone: FloodZone, db: Session) -> RiskScoreResponse:
    """
    Risk score = historical baseline + live crowd-report boost + live rainfall boost.
    """
    base = zone.historical_risk

    nearby_reports = db.query(ReportModel).filter(
        func.abs(ReportModel.lat - zone.lat) < 0.01,
        func.abs(ReportModel.lon - zone.lon) < 0.01,
    ).count()
    report_boost = min(nearby_reports * 0.5, 3)

    rain_mm = get_rainfall_mm(zone.lat, zone.lon)
    rain_boost = rainfall_risk_boost(rain_mm)

    score = min(base + report_boost + rain_boost, 10)

    if score >= 7:
        level = "high"
    elif score >= 4:
        level = "medium"
    else:
        level = "low"

    return RiskScoreResponse(
        zone_id=zone.id, name=zone.name, lat=zone.lat, lon=zone.lon,
        risk_score=score, risk_level=level, rainfall_mm=rain_mm,
    )


@app.get("/")
def root():
    return {"status": "ok", "service": "flood-advisor-api"}


@app.get("/zones", response_model=list[RiskScoreResponse])
def get_zones(db: Session = Depends(get_db)):
    """Get all flood zones with current risk score (historical + reports + live rainfall)."""
    zones = db.query(FloodZone).all()
    return [compute_risk(z, db) for z in zones]


@app.post("/report")
def submit_report(report: ReportIn, db: Session = Depends(get_db)):
    """User submits a live waterlogging report."""
    entry = ReportModel(
        id=str(uuid.uuid4()),
        lat=report.lat,
        lon=report.lon,
        severity=report.severity,
        note=report.note,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"status": "received", "report_id": entry.id}


@app.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    reports = db.query(ReportModel).all()
    return [
        {
            "id": r.id, "lat": r.lat, "lon": r.lon,
            "severity": r.severity, "note": r.note,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in reports
    ]


@app.post("/route-check")
def route_check(payload: RouteCheckIn, db: Session = Depends(get_db)):
    """
    Given a start and end point, warn if the route passes near any
    medium/high-risk flood zone. Uses straight-line sampling (MVP approximation).
    """
    zones = db.query(FloodZone).all()
    nearby = check_route(
        zones, payload.start_lat, payload.start_lon, payload.end_lat, payload.end_lon
    )

    warnings = []
    for entry in nearby:
        zone = entry["zone"]
        risk = compute_risk(zone, db)
        if risk.risk_level in ("medium", "high"):
            warnings.append({
                "zone_name": zone.name,
                "risk_level": risk.risk_level,
                "risk_score": risk.risk_score,
                "distance_km": entry["distance_km"],
            })

    warnings.sort(key=lambda w: w["risk_score"], reverse=True)

    return {
        "safe": len(warnings) == 0,
        "warnings": warnings,
    }
