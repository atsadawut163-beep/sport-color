import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Determine if we must enforce the configured database (no fallback)
enforce_db = (os.environ.get("RENDER") == "true") or (settings.DATABASE_URL is not None)

# Try to connect to MySQL/Postgres. If it fails, fall back to SQLite for easy offline testing in dev.
def initialize_engine():
    connect_args = {}
    db_url = settings.db_url
    if db_url.startswith("mysql"):
        # TiDB Cloud requires SSL connection. Enabling SSL in PyMySQL.
        connect_args = {"ssl": {}}
    
    try:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args=connect_args
        )
        # Test connection
        with engine.connect() as conn:
            pass
        print("Database: Connected to database successfully.")
        return engine
    except Exception as e:
        err_str = str(e)
        # 1049 is the MySQL error code for 'Unknown database'
        if "1049" in err_str and db_url.startswith("mysql"):
            print("Database Info: Target database not found. Attempting to create database 'sport_color_db'...")
            try:
                # Construct temporary URL pointing to 'sys' schema to run CREATE DATABASE
                parts = db_url.split("?")[0].split("/")
                base_url = "/".join(parts[:-1])
                query_params = "?" + db_url.split("?")[1] if "?" in db_url else ""
                sys_url = f"{base_url}/sys{query_params}"
                
                temp_engine = create_engine(sys_url, connect_args=connect_args)
                with temp_engine.connect() as conn:
                    from sqlalchemy import text
                    conn.execute(text("CREATE DATABASE IF NOT EXISTS sport_color_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                temp_engine.dispose()
                print("Database Success: Created database 'sport_color_db' successfully.")
                
                # Re-try main connection
                engine = create_engine(
                    db_url,
                    pool_pre_ping=True,
                    connect_args=connect_args
                )
                with engine.connect() as conn:
                    pass
                print("Database: Connected to database successfully after automatic creation.")
                return engine
            except Exception as create_err:
                print(f"Database Error: Failed to automatically create database: {create_err}")
        
        if enforce_db:
            print(f"Database Critical Error: Could not connect to configured database: {e}")
            raise e
        print(f"Database Warning: Could not connect to database: {e}")
        print("Database Fallback: Initializing local SQLite database 'sport_color_db.db' for demo...")
        sqlite_url = "sqlite:///./sport_color_db.db"
        return create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False}
        )

engine = initialize_engine()

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
