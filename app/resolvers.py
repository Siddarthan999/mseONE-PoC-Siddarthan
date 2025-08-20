from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Project

def get_projects(skip: int = 0, limit: int = 10, owner: str | None = None) -> list[Project]:
    db: Session = SessionLocal()
    try:
        query = db.query(Project)
        if owner:
            query = query.filter(Project.owner == owner)
        return query.offset(skip).limit(limit).all()
    finally:
        db.close()
