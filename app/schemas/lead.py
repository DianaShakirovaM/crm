from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class LeadBase(BaseModel):
    external_id: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(LeadBase):
    external_id: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class Lead(LeadBase):
    id: int
    created_at: datetime
    contact_count: Optional[int] = 0

    class Config:
        from_attributes = True
