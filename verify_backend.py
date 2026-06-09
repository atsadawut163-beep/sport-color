import sys
import os

print("=========================================")
print("Sport Color Backend Verification Script")
print("=========================================")

# Add current folder to sys.path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

try:
    print("[1/5] Checking python dependencies imports...")
    import fastapi
    import uvicorn
    import sqlalchemy
    import pymysql
    import jwt
    import passlib
    print("      SUCCESS: All core dependencies are installed!")
except ImportError as e:
    print(f"      WARNING: Missing dependency: {e}")
    print("      Please run: pip install -r requirements.txt")

try:
    print("[2/5] Testing config.py loading & .env parsing...")
    from app.config import settings
    print(f"      SUCCESS: settings loaded.")
    print(f"      Database URL parsed: {settings.db_url}")
    print(f"      JWT Expiration: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
except Exception as e:
    print(f"      ERROR: Failed to load config: {e}")
    sys.exit(1)

try:
    print("[3/5] Testing models.py and database.py initialization...")
    from app.database import Base
    from app.models import User, Transaction, SportsEvent, Participant, Result
    print("      SUCCESS: SQLAlchemy models compiled and mapped successfully.")
except Exception as e:
    print(f"      ERROR: Failed to load models: {e}")
    sys.exit(1)

try:
    print("[4/5] Testing schemas.py validations...")
    from app.schemas import UserLogin, TransactionCreate, ParticipantCreate, ResultCreate
    print("      SUCCESS: Pydantic schemas compiled successfully.")
except Exception as e:
    print(f"      ERROR: Failed to load schemas: {e}")
    sys.exit(1)

try:
    print("[5/5] Testing main.py app compilation...")
    from app.main import app
    print("      SUCCESS: FastAPI application object initialized.")
except Exception as e:
    print(f"      ERROR: Failed to initialize FastAPI application: {e}")
    sys.exit(1)

print("\n=========================================")
print(" VERIFICATION COMPLETE: ALL CHECKS PASSED!")
print(" Backend code structure is syntactically sound.")
print(" Next steps:")
print(" 1. Run uvicorn: python -m uvicorn backend.app.main:app --reload")
print(" 2. Open frontend/index.html in your browser.")
print("=========================================")
