from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime, date
from typing import List, Optional

# --- JWT Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# --- User Schemas ---
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4)
    full_name: Optional[str] = None
    role: str = "admin"

class UserUpdate(BaseModel):
    password: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    role: str
    
    model_config = ConfigDict(from_attributes=True)


# --- Transaction Schemas ---
class TransactionCreate(BaseModel):
    type: str = Field(..., description="'income' or 'expense'")
    category: str = Field(..., description="e.g. 'Equipment', 'Food', 'Uniform', 'Prizes'")
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    date: date

class TransactionResponse(BaseModel):
    id: int
    type: str
    category: str
    amount: Decimal
    description: Optional[str]
    date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Sports Event Schemas ---
class SportsEventCreate(BaseModel):
    name: str
    category: str
    status: str = "scheduled" # 'scheduled', 'ongoing', 'completed'
    schedule_time: Optional[datetime] = None

class SportsEventResponse(BaseModel):
    id: int
    name: str
    category: str
    status: str
    schedule_time: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Participant Schemas ---
class ParticipantCreate(BaseModel):
    name: str
    type: str = Field(..., description="'student' or 'staff'")
    color_team: str = Field(..., description="e.g. 'Red', 'Blue', 'Green', 'Yellow'")
    sport_event_id: Optional[int] = None

class ParticipantResponse(BaseModel):
    id: int
    name: str
    type: str
    color_team: str
    sport_event_id: Optional[int]
    sport_event_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Result Schemas ---
class ResultCreate(BaseModel):
    sport_event_id: int
    winner: str
    runner_up: Optional[str] = None
    second_runner_up: Optional[str] = None
    score: Optional[str] = None
    details: Optional[str] = None

class ResultResponse(BaseModel):
    id: int
    sport_event_id: int
    sport_event_name: str
    winner: str
    runner_up: Optional[str]
    second_runner_up: Optional[str]
    score: Optional[str]
    details: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Summary Schemas ---
class CategorySummary(BaseModel):
    category: str
    total: Decimal

class FinanceDashboardResponse(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    expenses_by_category: List[CategorySummary]
    recent_transactions: List[TransactionResponse]

class RosterParticipantItem(BaseModel):
    id: int
    name: str
    color_team: str
    sport_event_name: Optional[str] = None

class RosterDashboardResponse(BaseModel):
    students: List[RosterParticipantItem]
    staff: List[RosterParticipantItem]
    total_members: int = 0



# --- Member Schemas ---
class MemberCreate(BaseModel):
    name: str
    type: str = Field(..., description="'student' or 'staff' (นักเรียน / บุคลากร)")
    amount: Decimal = Field(..., gt=0)
    status: str = "unpaid" # 'paid' or 'unpaid'

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[Decimal] = None
    status: Optional[str] = None

class MemberResponse(BaseModel):
    id: int
    name: str
    type: str
    amount: Decimal
    status: str
    transaction_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Sports Roster Schemas ---
class SportParticipantItem(BaseModel):
    id: int
    name: str
    type: str
    color_team: str

    model_config = ConfigDict(from_attributes=True)

class SportWithParticipantsResponse(BaseModel):
    id: int
    name: str
    category: str
    status: str
    participants: List[SportParticipantItem]

    model_config = ConfigDict(from_attributes=True)

