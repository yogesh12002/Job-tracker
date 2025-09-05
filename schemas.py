from pydantic import BaseModel
from datetime import date
from typing import Optional

class ApplicationBase(BaseModel):
    company_name: str
    role: str
    platform: str
    date_applied: date
    status: Optional[str] = "Applied"
    job_link: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    status: str

class ApplicationOut(ApplicationBase):
    id: int

    class Config:
        from_attributes = True
