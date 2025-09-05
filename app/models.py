from sqlalchemy import Column, Integer, String, Date
from database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    role = Column(String)
    platform = Column(String)
    date_applied = Column(Date)
    status = Column(String, default="Applied")
    job_link = Column(String)
