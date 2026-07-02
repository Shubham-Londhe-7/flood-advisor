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
