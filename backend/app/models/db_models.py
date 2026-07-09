"""
SQLAlchemy ORM models for Neon Postgres.
Tables: interactions, hcp_profiles
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hcp_name = Column(String(255), nullable=False)
    interaction_type = Column(String(50), nullable=False, default="Meeting")
    date = Column(String(20), nullable=True)
    time = Column(String(10), nullable=True)
    attendees = Column(JSON, default=list)
    topics_discussed = Column(Text, default="")
    materials_shared = Column(JSON, default=list)
    samples_distributed = Column(JSON, default=list)
    sentiment = Column(String(20), default="Neutral")
    outcomes = Column(Text, default="")
    follow_up_actions = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Interaction(id={self.id}, hcp={self.hcp_name}, type={self.interaction_type})>"


class HCPProfileModel(Base):
    __tablename__ = "hcp_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    specialty = Column(String(255), default="")
    tier = Column(String(20), default="")
    last_interaction_sentiment = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<HCPProfile(id={self.id}, name={self.name}, specialty={self.specialty})>"
