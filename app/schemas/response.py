from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from .lead import Lead
from .operator import Operator
from .source import Source


class ContactWithDetails(BaseModel):
    id: int
    lead_external_id: str
    source_id: int
    message: Optional[str] = None
    lead_email: Optional[EmailStr] = None
    lead_phone: Optional[str] = None
    lead_id: int
    operator_id: Optional[int]
    is_active: bool
    created_at: datetime
    lead: Lead
    source: Source
    operator: Optional[Operator] = None


class LeadWithContacts(BaseModel):
    id: int
    external_id: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    created_at: datetime
    contact_count: Optional[int] = 0
    contacts: List[ContactWithDetails] = []


class SourceWithWeights(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    operator_weights: List[dict] = []
