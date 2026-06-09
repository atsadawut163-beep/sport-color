from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default="admin")
    created_at = Column(DateTime, server_default=func.now())


class SportsEvent(Base):
    __tablename__ = "sports_events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False) # e.g., 'Indoor', 'Outdoor', 'Track'
    status = Column(String(50), default="scheduled") # 'scheduled', 'ongoing', 'completed'
    schedule_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    participants = relationship("Participant", back_populates="sport_event", cascade="all, delete-orphan")
    result = relationship("Result", back_populates="sport_event", uselist=False, cascade="all, delete-orphan")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False) # 'student' or 'staff'
    color_team = Column(String(50), nullable=False) # 'Red', 'Blue', 'Green', 'Yellow'
    sport_event_id = Column(Integer, ForeignKey("sports_events.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    sport_event = relationship("SportsEvent", back_populates="participants")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False) # 'income' or 'expense'
    category = Column(String(50), nullable=False) # e.g. 'Equipment', 'Food', 'Uniform', 'Prizes'
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(255), nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    sport_event_id = Column(Integer, ForeignKey("sports_events.id", ondelete="CASCADE"), unique=True, nullable=False)
    winner = Column(String(100), nullable=False)
    runner_up = Column(String(100), nullable=True)
    second_runner_up = Column(String(100), nullable=True)
    score = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    sport_event = relationship("SportsEvent", back_populates="result")


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False) # 'student' or 'member' (นักเรียน / สมาชิก)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="unpaid") # 'paid' or 'unpaid'
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    transaction = relationship("Transaction")
