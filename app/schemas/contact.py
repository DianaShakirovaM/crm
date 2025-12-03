from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class ContactBase(BaseModel):
    lead_external_id: str
    source_id: int
    message: Optional[str] = None
    lead_email: Optional[EmailStr] = None
    lead_phone: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    is_active: Optional[bool] = None
    operator_id: Optional[int] = None


class Contact(ContactBase):
    id: int
    lead_id: int
    operator_id: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ContactStatusUpdate(BaseModel):
    is_active: bool
