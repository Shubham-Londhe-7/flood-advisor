"""
Database setup - SQLAlchemy models + connection, reads DATABASE_URL from .env
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FloodZone(Base):
    __tablename__ = "flood_zones"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    historical_risk = Column(Integer, nullable=False)


class Report(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    severity = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create tables if not exist, seed flood_zones if empty."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(FloodZone).count() == 0:
            seed_zones = [
                FloodZone(id="1", name="Sinhagad Road (near market)", lat=18.4886, lon=73.8225, historical_risk=4),
                FloodZone(id="2", name="Karve Road Underpass", lat=18.5034, lon=73.8188, historical_risk=5),
                FloodZone(id="3", name="Bibwewadi Underpass", lat=18.4713, lon=73.8590, historical_risk=4),
                FloodZone(id="4", name="Warje Naka", lat=18.4700, lon=73.8074, historical_risk=3),
                FloodZone(id="5", name="Dhankawadi Katraj Road", lat=18.4570, lon=73.8560, historical_risk=3),
                # Added from real PMC/news-reported hotspots (2025 monsoon)
                FloodZone(id="6", name="Kothrud", lat=18.5074, lon=73.8077, historical_risk=3),
                FloodZone(id="7", name="Karvenagar", lat=18.4837, lon=73.8148, historical_risk=3),
                FloodZone(id="8", name="Bavdhan", lat=18.5089, lon=73.7749, historical_risk=3),
                FloodZone(id="9", name="Aundh", lat=18.5590, lon=73.8080, historical_risk=3),
                FloodZone(id="10", name="Bopodi (Bhau Patil Road)", lat=18.5622, lon=73.8420, historical_risk=4),
                FloodZone(id="11", name="Hadapsar", lat=18.5089, lon=73.9260, historical_risk=3),
                FloodZone(id="12", name="Yerawada", lat=18.5580, lon=73.8790, historical_risk=3),
                FloodZone(id="13", name="Baner", lat=18.5590, lon=73.7870, historical_risk=3),
                FloodZone(id="14", name="Balewadi", lat=18.5730, lon=73.7700, historical_risk=3),
                FloodZone(id="15", name="Kondhwa", lat=18.4650, lon=73.8930, historical_risk=3),
                FloodZone(id="16", name="Navale Bridge / NH area", lat=18.4630, lon=73.8110, historical_risk=4),
                FloodZone(id="17", name="Khadakwasla / Dhayari Narhe", lat=18.4520, lon=73.7770, historical_risk=4),
            ]
            db.add_all(seed_zones)
            db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
