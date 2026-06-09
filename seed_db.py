import sys
import os

print("Running manual seeding script...")

# Add backend to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

try:
    from app.database import SessionLocal, Base, engine
    from app.crud import seed_default_admin
    from app import models
    
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    print("Tables verified/created successfully.")
    
    # Seed
    db = SessionLocal()
    try:
        seed_default_admin(db)
        print("Manual seeding completed successfully!")
        
        # Verify
        from app.models import User
        users = db.query(User).all()
        print(f"Current users in DB: {[u.username for u in users]}")
    finally:
        db.close()
except Exception as e:
    print(f"Error seeding database: {e}")
    sys.exit(1)
