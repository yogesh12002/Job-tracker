from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime
from app.database import Base  # absolute import

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    role = Column(String, default="Not specified")
    platform = Column(String, default="Not specified")
    date_applied = Column(Date)
    status = Column(String, default="Applied")
    job_link = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
