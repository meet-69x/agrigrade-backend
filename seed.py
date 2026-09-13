"""
Run this once after the API is up to create a starter centre + admin user
so the frontend has something real to log in with immediately.

Usage (with the stack running via docker compose):
    docker compose exec api python seed.py
"""
from app.database import SessionLocal, Base, engine
from app.models.centre import Centre
from app.models.user import User, UserRole
from app.auth.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

centre = db.query(Centre).filter(Centre.name == "Nashik Procurement Centre").first()
if not centre:
    centre = Centre(name="Nashik Procurement Centre", location="Nashik, Maharashtra")
    db.add(centre)
    db.commit()
    db.refresh(centre)
    print(f"Created centre: {centre.id}")

admin = db.query(User).filter(User.email == "admin@agrigrade.ai").first()
if not admin:
    admin = User(
        name="Admin User",
        email="admin@agrigrade.ai",
        password_hash=hash_password("admin123"),
        role=UserRole.admin,
        centre_id=centre.id,
    )
    db.add(admin)
    db.commit()
    print("Created admin user -> email: admin@agrigrade.ai / password: admin123")
else:
    print("Admin user already exists.")

db.close()
