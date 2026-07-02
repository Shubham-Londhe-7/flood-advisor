"""
Pune Flood/Waterlogging Advisor - Backend
Now backed by Postgres (Supabase) via SQLAlchemy - see database.py
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from database import init_db, get_db, FloodZone, Report as ReportModel

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


class Report(BaseModel):
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


def compute_risk(zone: FloodZone, db: Session) -> RiskScoreResponse:
    """
    Risk score = historical baseline + live report boost.
    Phase 2: add rainfall API weight here.
    """
    base = zone.historical_risk

    nearby_reports = db.query(ReportModel).filter(
        func.abs(ReportModel.lat - zone.lat) < 0.01,
        func.abs(ReportModel.lon - zone.lon) < 0.01,
    ).count()

    report_boost = min(nearby_reports * 0.5, 3)
    score = min(base + report_boost, 10)

    if score >= 7:
        level = "high"
    elif score >= 4:
        level = "medium"
    else:
        level = "low"

    return RiskScoreResponse(
        zone_id=zone.id, name=zone.name, lat=zone.lat, lon=zone.lon,
        risk_score=score, risk_level=level,
    )


@app.get("/")
def root():
    return {"status": "ok", "service": "flood-advisor-api"}


@app.get("/zones", response_model=list[RiskScoreResponse])
def get_zones(db: Session = Depends(get_db)):
    """Get all flood zones with current risk score."""
    zones = db.query(FloodZone).all()
    return [compute_risk(z, db) for z in zones]


@app.post("/report")
def submit_report(report: Report, db: Session = Depends(get_db)):
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


# TODO Phase 2: pull live rainfall from OpenWeatherMap/IMD, add to compute_risk()
# TODO Phase 3: route-check endpoint — given start/end lat-lon, check if path crosses high-risk zone
