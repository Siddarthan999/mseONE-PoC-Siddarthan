from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner = Column(String, index=True)
    created_at = Column(DateTime, server_default=func.now())
