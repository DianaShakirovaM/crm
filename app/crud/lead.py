from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.contact import Contact
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate


class CRUDLead(CRUDBase[Lead, LeadCreate, LeadUpdate]):
    def get_by_external_id(
        self, db: Session, *, external_id: str
    ) -> Optional[Lead]:
        return db.query(Lead).filter(Lead.external_id == external_id).first()

    def get_or_create(
        self, db: Session, *, external_id: str,
        email: Optional[str] = None, phone: Optional[str] = None
    ) -> Lead:
        lead = self.get_by_external_id(db, external_id=external_id)
        if not lead:
            lead_in = LeadCreate(
                external_id=external_id, email=email, phone=phone)
            lead = self.create(db, obj_in=lead_in)
        elif email or phone:
            update_data = {}
            if email:
                update_data['email'] = email
            if phone:
                update_data['phone'] = phone
            if update_data:
                lead = self.update(db, db_obj=lead, obj_in=update_data)
        return lead

    def get_with_contact_count(
        self, db: Session, *, lead_id: int
    ) -> Optional[Lead]:
        lead = self.get(db, id=lead_id)
        if lead:
            contact_count = db.query(func.count(Contact.id)).filter(
                Contact.lead_id == lead_id
            ).scalar()
            setattr(lead, 'contact_count', contact_count)
        return lead

    def get_multi_with_contact_count(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Lead]:
        leads = self.get_multi(db, skip=skip, limit=limit)
        for lead in leads:
            contact_count = db.query(func.count(Contact.id)).filter(
                Contact.lead_id == lead.id
            ).scalar()
            setattr(lead, 'contact_count', contact_count)
        return leads


lead = CRUDLead(Lead)
