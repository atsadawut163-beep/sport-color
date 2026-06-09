from sqlalchemy import func
from sqlalchemy.orm import Session
from decimal import Decimal
import datetime

from app import models, schemas, auth

# --- User Management ---
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def seed_default_admin(db: Session):
    """Seed the default administrator user if it doesn't exist."""
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        hashed_password = auth.get_password_hash("Prtc2026")
        admin = models.User(
            username="admin",
            password_hash=hashed_password,
            full_name="System Administrator",
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Default administrator seeded successfully (admin / Prtc2026).")

def get_users(db: Session):
    return db.query(models.User).order_by(models.User.username.asc()).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    if user_update.password:
        db_user.password_hash = auth.get_password_hash(user_update.password)
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    if user_update.role is not None:
        db_user.role = user_update.role
        
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int, current_username: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return {"status": "error", "message": "User not found"}
        
    # Safety Check: Cannot delete self
    if db_user.username == current_username:
        return {"status": "error", "message": "You cannot delete your own account."}
        
    # Safety Check: Cannot delete last remaining admin
    admin_count = db.query(models.User).filter(models.User.role == "admin").count()
    if db_user.role == "admin" and admin_count <= 1:
        return {"status": "error", "message": "Cannot delete the last remaining admin."}
        
    db.delete(db_user)
    db.commit()
    return {"status": "success", "message": "User deleted successfully"}


# --- Transactions CRUD ---
def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_tx = models.Transaction(
        type=transaction.type,
        category=transaction.category,
        amount=transaction.amount,
        description=transaction.description,
        date=transaction.date
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

def get_transactions(db: Session, limit: int = 100):
    return db.query(models.Transaction).order_by(models.Transaction.date.desc(), models.Transaction.id.desc()).limit(limit).all()

def get_finance_summary(db: Session) -> dict:
    # 1. Total Income
    total_income = db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.type == "income").scalar() or Decimal("0.00")
    
    # 2. Total Expense
    total_expense = db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.type == "expense").scalar() or Decimal("0.00")
    
    # 3. Balance
    balance = total_income - total_expense
    
    # 4. Expenses by Category
    category_rows = db.query(
        models.Transaction.category,
        func.sum(models.Transaction.amount).label("total")
    ).filter(models.Transaction.type == "expense").group_by(models.Transaction.category).all()
    
    expenses_by_category = [
        {"category": row[0], "total": row[1] or Decimal("0.00")}
        for row in category_rows
    ]
    
    # 5. Recent transactions (limit 10)
    recent_txs = db.query(models.Transaction).order_by(models.Transaction.date.desc(), models.Transaction.id.desc()).limit(10).all()
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "expenses_by_category": expenses_by_category,
        "recent_transactions": recent_txs
    }


# --- Sports Events CRUD ---
def create_sports_event(db: Session, event: schemas.SportsEventCreate):
    db_event = models.SportsEvent(
        name=event.name,
        category=event.category,
        status=event.status,
        schedule_time=event.schedule_time
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_sports_events(db: Session):
    return db.query(models.SportsEvent).order_by(models.SportsEvent.name.asc()).all()


# --- Participants CRUD ---
def create_participant(db: Session, participant: schemas.ParticipantCreate):
    db_participant = models.Participant(
        name=participant.name,
        type=participant.type,
        color_team=participant.color_team,
        sport_event_id=participant.sport_event_id
    )
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant

def get_participants_roster(db: Session) -> dict:
    participants = db.query(models.Participant).all()
    members = db.query(models.Member).all()
    
    students = []
    staff = []
    
    for p in participants:
        sport_name = p.sport_event.name if p.sport_event else "General / No Sport"
        item = {
            "id": p.id,
            "name": p.name,
            "color_team": p.color_team,
            "sport_event_name": sport_name
        }
        if p.type == "student":
            students.append(item)
        else:
            staff.append(item)
            
    for m in members:
        status_text = "ชำระเงินแล้ว" if m.status == "paid" else "ยังไม่ได้ชำระ"
        item = {
            "id": m.id,
            "name": m.name,
            "color_team": "สมาชิก",
            "sport_event_name": f"สมาชิก ({status_text})"
        }
        if m.type == "student":
            students.append(item)
        else:
            staff.append(item)
            
    return {
        "students": students,
        "staff": staff,
        "total_members": len(members)
    }



# --- Results CRUD ---
def create_or_update_result(db: Session, result: schemas.ResultCreate):
    # Check if a result already exists for this sport event
    db_result = db.query(models.Result).filter(models.Result.sport_event_id == result.sport_event_id).first()
    
    if db_result:
        db_result.winner = result.winner
        db_result.runner_up = result.runner_up
        db_result.second_runner_up = result.second_runner_up
        db_result.score = result.score
        db_result.details = result.details
    else:
        db_result = models.Result(
            sport_event_id=result.sport_event_id,
            winner=result.winner,
            runner_up=result.runner_up,
            second_runner_up=result.second_runner_up,
            score=result.score,
            details=result.details
        )
        db.add(db_result)
        
    db.commit()
    db.refresh(db_result)
    
    # Also update the corresponding sports event status to 'completed'
    sport_event = db.query(models.SportsEvent).filter(models.SportsEvent.id == result.sport_event_id).first()
    if sport_event:
        sport_event.status = "completed"
        db.commit()
        
    return db_result

def get_results_summary(db: Session):
    results = db.query(models.Result).all()
    summary = []
    for r in results:
        sport_name = r.sport_event.name if r.sport_event else "Unknown Sport"
        summary.append({
            "id": r.id,
            "sport_event_id": r.sport_event_id,
            "sport_event_name": sport_name,
            "winner": r.winner,
            "runner_up": r.runner_up,
            "second_runner_up": r.second_runner_up,
            "score": r.score,
            "details": r.details,
            "created_at": r.created_at
        })
    return summary


# --- Sports & Results CRUD Extensions ---

def update_sports_event(db: Session, event_id: int, event_update: schemas.SportsEventCreate):
    db_event = db.query(models.SportsEvent).filter(models.SportsEvent.id == event_id).first()
    if not db_event:
        return None
    db_event.name = event_update.name
    db_event.category = event_update.category
    db_event.status = event_update.status
    if event_update.schedule_time:
        db_event.schedule_time = event_update.schedule_time
    db.commit()
    db.refresh(db_event)
    return db_event

def delete_sports_event(db: Session, event_id: int):
    db_event = db.query(models.SportsEvent).filter(models.SportsEvent.id == event_id).first()
    if not db_event:
        return False
    db.delete(db_event)
    db.commit()
    return True

def delete_result(db: Session, result_id: int):
    db_result = db.query(models.Result).filter(models.Result.id == result_id).first()
    if not db_result:
        return False
    
    # Reset corresponding event status back to 'ongoing'
    sport_event = db.query(models.SportsEvent).filter(models.SportsEvent.id == db_result.sport_event_id).first()
    if sport_event:
        sport_event.status = "ongoing"
        db.commit()
        
    db.delete(db_result)
    db.commit()
    return True


# --- Member CRUD & Sync ---

def get_members(db: Session):
    return db.query(models.Member).order_by(models.Member.created_at.desc()).all()

def create_member(db: Session, member: schemas.MemberCreate):
    db_member = models.Member(
        name=member.name,
        type=member.type,
        amount=member.amount,
        status=member.status
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    
    # Finance Sync: Create income transaction if paid
    if member.status == "paid":
        tx = models.Transaction(
            type="income",
            category="ค่าสมาชิก",
            amount=member.amount,
            description=f"ค่าสมาชิก: {member.name} ({'นักเรียน' if member.type == 'student' else 'บุคลากร'})",
            date=datetime.date.today()
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        db_member.transaction_id = tx.id
        db.commit()
        db.refresh(db_member)
        
    return db_member

def update_member(db: Session, member_id: int, member_update: schemas.MemberUpdate):
    db_member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not db_member:
        return None
        
    old_status = db_member.status
    old_amount = db_member.amount
    
    # Update fields if provided
    if member_update.name is not None:
        db_member.name = member_update.name
    if member_update.type is not None:
        db_member.type = member_update.type
    if member_update.amount is not None:
        db_member.amount = member_update.amount
    if member_update.status is not None:
        db_member.status = member_update.status
        
    db.commit()
    db.refresh(db_member)
    
    # Finance Sync Transitions:
    # 1. unpaid -> paid
    if old_status == "unpaid" and db_member.status == "paid":
        tx = models.Transaction(
            type="income",
            category="ค่าสมาชิก",
            amount=db_member.amount,
            description=f"ค่าสมาชิก: {db_member.name} ({'นักเรียน' if db_member.type == 'student' else 'บุคลากร'})",
            date=datetime.date.today()
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        db_member.transaction_id = tx.id
        db.commit()
        db.refresh(db_member)
        
    # 2. paid -> unpaid
    elif old_status == "paid" and db_member.status == "unpaid":
        if db_member.transaction_id:
            tx = db.query(models.Transaction).filter(models.Transaction.id == db_member.transaction_id).first()
            if tx:
                db.delete(tx)
            db_member.transaction_id = None
            db.commit()
            db.refresh(db_member)
            
    # 3. paid -> paid, but amount or details changed
    elif old_status == "paid" and db_member.status == "paid":
        if db_member.transaction_id:
            tx = db.query(models.Transaction).filter(models.Transaction.id == db_member.transaction_id).first()
            if tx:
                tx.amount = db_member.amount
                tx.description = f"ค่าสมาชิก: {db_member.name} ({'นักเรียน' if db_member.type == 'student' else 'บุคลากร'})"
                db.commit()
                
    return db_member

def delete_member(db: Session, member_id: int):
    db_member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not db_member:
        return False
        
    # Finance Sync: Delete transaction if exists
    if db_member.transaction_id:
        tx = db.query(models.Transaction).filter(models.Transaction.id == db_member.transaction_id).first()
        if tx:
            db.delete(tx)
            
    db.delete(db_member)
    db.commit()
    return True


# --- Additional CRUD Extensions ---

def update_transaction(db: Session, transaction_id: int, transaction_update: schemas.TransactionCreate):
    db_tx = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not db_tx:
        return None
    db_tx.type = transaction_update.type
    db_tx.category = transaction_update.category
    db_tx.amount = transaction_update.amount
    db_tx.description = transaction_update.description
    db_tx.date = transaction_update.date
    db.commit()
    db.refresh(db_tx)
    return db_tx

def delete_transaction(db: Session, transaction_id: int) -> bool:
    db_tx = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not db_tx:
        return False
    db.delete(db_tx)
    db.commit()
    return True

def get_participants(db: Session):
    return db.query(models.Participant).order_by(models.Participant.created_at.desc()).all()

def update_participant(db: Session, participant_id: int, participant_update: schemas.ParticipantCreate):
    db_p = db.query(models.Participant).filter(models.Participant.id == participant_id).first()
    if not db_p:
        return None
    db_p.name = participant_update.name
    db_p.type = participant_update.type
    db_p.color_team = participant_update.color_team
    db_p.sport_event_id = participant_update.sport_event_id
    db.commit()
    db.refresh(db_p)
    return db_p

def delete_participant(db: Session, participant_id: int) -> bool:
    db_p = db.query(models.Participant).filter(models.Participant.id == participant_id).first()
    if not db_p:
        return False
    db.delete(db_p)
    db.commit()
    return True

def get_sports_with_participants(db: Session):
    events = db.query(models.SportsEvent).order_by(models.SportsEvent.name.asc()).all()
    result = []
    for event in events:
        result.append({
            "id": event.id,
            "name": event.name,
            "category": event.category,
            "status": event.status,
            "participants": [
                {
                    "id": p.id,
                    "name": p.name,
                    "type": p.type,
                    "color_team": p.color_team
                }
                for p in event.participants
            ]
        })
    return result

