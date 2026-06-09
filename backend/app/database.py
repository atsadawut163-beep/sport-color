from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Try to connect to MySQL. If it fails, fall back to SQLite for easy offline testing.
try:
    connect_args = {}
    if settings.db_url.startswith("mysql"):
        # TiDB Cloud requires SSL connection. Enabling SSL in PyMySQL.
        connect_args = {"ssl": {}}
    engine = create_engine(
        settings.db_url,
        pool_pre_ping=True,
        connect_args=connect_args
    )
    # Test connection
    with engine.connect() as conn:
        pass
    print("Database: Connected to MySQL database successfully.")
except Exception as e:
    print(f"Database Warning: Could not connect to MySQL: {e}")
    print("Database Fallback: Initializing local SQLite database 'sport_color_db.db' for demo...")
    # SQLite URL
    sqlite_url = "sqlite:///./sport_color_db.db"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False}
    )

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models
Base = declarative_base()

# DB Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
