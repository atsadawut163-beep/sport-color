from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models, schemas, crud, auth
from app.database import Base, engine, get_db, SessionLocal
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events to handle DB table creation and seeding on startup."""
    print("Initializing Database...")
    try:
        # Create tables if they do not exist
        Base.metadata.create_all(bind=engine)
        
        # Seed default admin user
        db = SessionLocal()
        try:
            crud.seed_default_admin(db)
        finally:
            db.close()
    except Exception as e:
        print(f"CRITICAL: Could not connect to database or create tables: {e}")
        print("Please check your MySQL configuration in the .env file and ensure MySQL server is running.")
    yield

app = FastAPI(
    title="Sport Color Event & Finance Dashboard API",
    description="Backend API for managing school color sports day events, participants, results, and budget details.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
# Crucial to allow frontend index.html/admin.html opened directly via local files (file://) or other origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "status": "success",
        "message": "Sport Color Event & Finance API is running.",
        "documentation": "/docs"
    }


# --- Authentication Route ---
@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, login_data.username)
    if not user or not auth.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- Admin Protected Routes ---

# --- Admin User Management Endpoints ---

@app.get("/api/admin/users", response_model=List[schemas.UserResponse])
def list_admins(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Retrieve list of all administrators."""
    return crud.get_users(db=db)


@app.post("/api/admin/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def add_admin(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Register a new administrator."""
    existing_user = crud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered."
        )
    return crud.create_user(db=db, user=user_data)


@app.put("/api/admin/users/{user_id}", response_model=schemas.UserResponse)
def modify_admin(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Update details of an administrator account."""
    updated = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found."
        )
    return updated


@app.delete("/api/admin/users/{user_id}")
def remove_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Delete an administrator account."""
    result = crud.delete_user(db=db, user_id=user_id, current_username=current_user.username)
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return {"status": "success", "message": result["message"]}


@app.post("/api/admin/transactions", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def add_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Record a new financial transaction (Income or Expense)."""
    return crud.create_transaction(db=db, transaction=transaction)


@app.post("/api/admin/participants", response_model=schemas.ParticipantResponse, status_code=status.HTTP_201_CREATED)
def add_participant(
    participant: schemas.ParticipantCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Register a new participant (Student or Staff) and optionally assign to a sport event."""
    db_participant = crud.create_participant(db=db, participant=participant)
    
    # Return formatted response
    sport_name = db_participant.sport_event.name if db_participant.sport_event else None
    return schemas.ParticipantResponse(
        id=db_participant.id,
        name=db_participant.name,
        type=db_participant.type,
        color_team=db_participant.color_team,
        sport_event_id=db_participant.sport_event_id,
        sport_event_name=sport_name,
        created_at=db_participant.created_at
    )


@app.post("/api/admin/results", response_model=schemas.ResultResponse, status_code=status.HTTP_201_CREATED)
def update_result(
    result: schemas.ResultCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Post or update the results of a sports event. Marks the event as completed."""
    db_result = crud.create_or_update_result(db=db, result=result)
    sport_name = db_result.sport_event.name if db_result.sport_event else "Unknown Sport"
    return schemas.ResultResponse(
        id=db_result.id,
        sport_event_id=db_result.sport_event_id,
        sport_event_name=sport_name,
        winner=db_result.winner,
        runner_up=db_result.runner_up,
        second_runner_up=db_result.second_runner_up,
        score=db_result.score,
        details=db_result.details,
        created_at=db_result.created_at
    )


@app.post("/api/admin/sports-events", response_model=schemas.SportsEventResponse, status_code=status.HTTP_201_CREATED)
def add_sports_event(
    event: schemas.SportsEventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Create a new sports competition event."""
    return crud.create_sports_event(db=db, event=event)

@app.post("/api/admin/sports-events/bulk", response_model=List[schemas.SportsEventResponse], status_code=status.HTTP_201_CREATED)
def add_sports_events_bulk(
    events: List[schemas.SportsEventCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Create multiple sports events in bulk."""
    created_events = []
    for event in events:
        db_event = crud.create_sports_event(db=db, event=event)
        created_events.append(db_event)
    return created_events


# --- Sports & Results CRUD Extensions ---

@app.put("/api/admin/sports-events/{event_id}", response_model=schemas.SportsEventResponse)
def modify_sports_event(
    event_id: int,
    event_update: schemas.SportsEventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Update a sports event's details."""
    db_event = crud.update_sports_event(db=db, event_id=event_id, event_update=event_update)
    if not db_event:
        raise HTTPException(status_code=404, detail="Sports event not found")
    return db_event

@app.delete("/api/admin/sports-events/{event_id}")
def remove_sports_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Delete a sports event and its linked results."""
    success = crud.delete_sports_event(db=db, event_id=event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sports event not found")
    return {"status": "success", "message": "Sports event deleted successfully"}

@app.delete("/api/admin/results/{result_id}")
def remove_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Delete a sport event's result record and reset its status to ongoing."""
    success = crud.delete_result(db=db, result_id=result_id)
    if not success:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"status": "success", "message": "Result deleted and event status reverted successfully"}


# --- Member CRUD Endpoints ---

@app.get("/api/admin/members", response_model=List[schemas.MemberResponse])
def list_members(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Retrieve list of all members."""
    return crud.get_members(db=db)

@app.post("/api/admin/members", response_model=schemas.MemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    member_data: schemas.MemberCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Register a new member and sync with budget if paid."""
    return crud.create_member(db=db, member=member_data)

@app.post("/api/admin/members/bulk", response_model=List[schemas.MemberResponse], status_code=status.HTTP_201_CREATED)
def add_members_bulk(
    members_data: List[schemas.MemberCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Register multiple members at once."""
    created_members = []
    for member in members_data:
        db_member = crud.create_member(db=db, member=member)
        created_members.append(db_member)
    return created_members

@app.put("/api/admin/members/{member_id}", response_model=schemas.MemberResponse)
def modify_member(
    member_id: int,
    member_update: schemas.MemberUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Update details or payment status of a member."""
    updated = crud.update_member(db=db, member_id=member_id, member_update=member_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Member not found")
    return updated

@app.delete("/api/admin/members/{member_id}")
def remove_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Unregister a member and delete associated budget logs."""
    success = crud.delete_member(db=db, member_id=member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"status": "success", "message": "Member deleted successfully"}


# --- Public Dashboard Routes ---

@app.get("/api/public/dashboard/finance", response_model=schemas.FinanceDashboardResponse)
def get_finance_dashboard(db: Session = Depends(get_db)):
    """Fetch financial summary for dashboard charts and widgets."""
    return crud.get_finance_summary(db=db)


@app.get("/api/public/dashboard/results", response_model=List[schemas.ResultResponse])
def get_results_dashboard(db: Session = Depends(get_db)):
    """Fetch all recorded event results."""
    raw_results = crud.get_results_summary(db=db)
    
    # Map raw results into the Pydantic Response schemas
    response = []
    for r in raw_results:
        response.append(schemas.ResultResponse(
            id=r["id"],
            sport_event_id=r["sport_event_id"],
            sport_event_name=r["sport_event_name"],
            winner=r["winner"],
            runner_up=r["runner_up"],
            second_runner_up=r["second_runner_up"],
            score=r["score"],
            details=r["details"],
            created_at=r["created_at"]
        ))
    return response


@app.get("/api/public/dashboard/roster", response_model=schemas.RosterDashboardResponse)
def get_roster_dashboard(db: Session = Depends(get_db)):
    """Fetch the list of participants divided into students and staff."""
    return crud.get_participants_roster(db=db)


@app.get("/api/public/sports", response_model=List[schemas.SportsEventResponse])
def list_sports_events(db: Session = Depends(get_db)):
    """Fetch the list of all sports events."""
    return crud.get_sports_events(db=db)


# --- Additional Admin & Public Endpoints ---

@app.get("/api/admin/transactions", response_model=List[schemas.TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Retrieve list of all transactions."""
    return db.query(models.Transaction).order_by(models.Transaction.date.desc(), models.Transaction.id.desc()).limit(200).all()

@app.put("/api/admin/transactions/{transaction_id}", response_model=schemas.TransactionResponse)
def update_existing_transaction(
    transaction_id: int,
    transaction_update: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Update an existing transaction."""
    tx = crud.update_transaction(db=db, transaction_id=transaction_id, transaction_update=transaction_update)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@app.delete("/api/admin/transactions/{transaction_id}")
def delete_existing_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Delete a transaction."""
    success = crud.delete_transaction(db=db, transaction_id=transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"status": "success", "message": "Transaction deleted successfully"}

@app.get("/api/admin/participants", response_model=List[schemas.ParticipantResponse])
def list_participants(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Retrieve all participants (raw list for admin CRUD)."""
    participants = crud.get_participants(db=db)
    response = []
    for p in participants:
        sport_name = p.sport_event.name if p.sport_event else None
        response.append(schemas.ParticipantResponse(
            id=p.id,
            name=p.name,
            type=p.type,
            color_team=p.color_team,
            sport_event_id=p.sport_event_id,
            sport_event_name=sport_name,
            created_at=p.created_at
        ))
    return response

@app.put("/api/admin/participants/{participant_id}", response_model=schemas.ParticipantResponse)
def modify_participant(
    participant_id: int,
    participant_update: schemas.ParticipantCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Update a participant's registration."""
    db_p = crud.update_participant(db=db, participant_id=participant_id, participant_update=participant_update)
    if not db_p:
        raise HTTPException(status_code=404, detail="Participant not found")
    sport_name = db_p.sport_event.name if db_p.sport_event else None
    return schemas.ParticipantResponse(
        id=db_p.id,
        name=db_p.name,
        type=db_p.type,
        color_team=db_p.color_team,
        sport_event_id=db_p.sport_event_id,
        sport_event_name=sport_name,
        created_at=db_p.created_at
    )

@app.delete("/api/admin/participants/{participant_id}")
def remove_participant(
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Delete a participant."""
    success = crud.delete_participant(db=db, participant_id=participant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Participant not found")
    return {"status": "success", "message": "Participant deleted successfully"}

@app.get("/api/public/sports-roster", response_model=List[schemas.SportWithParticipantsResponse])
def get_sports_roster(db: Session = Depends(get_db)):
    """Fetch all sports events and their registered participant roster details."""
    return crud.get_sports_with_participants(db=db)

@app.get("/api/public/debug-db")
def debug_db(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        return {
            "dialect": db.bind.dialect.name,
            "tables": inspector.get_table_names(),
            "db_url_masked": str(db.bind.url).split("@")[-1]
        }
    except Exception as e:
        return {"error": str(e)}

