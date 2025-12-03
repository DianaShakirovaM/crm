from typing import Dict, List, Optional

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


class CRUDContact(CRUDBase[Contact, ContactCreate, ContactUpdate]):
    def get_by_lead_id(self, db: Session, *, lead_id: int) -> List[Contact]:
        return db.query(Contact).filter(Contact.lead_id == lead_id).all()

    def get_by_operator_id(
        self, db: Session, *, operator_id: int
    ) -> List[Contact]:
        return db.query(Contact).filter(
            Contact.operator_id == operator_id).all()

    def get_active_by_operator(
        self, db: Session, *, operator_id: int
    ) -> List[Contact]:
        return db.query(Contact).filter(
            Contact.operator_id == operator_id,
            Contact.is_active == True
        ).all()

    def get_by_source_id(
        self, db: Session, *, source_id: int
    ) -> List[Contact]:
        return db.query(Contact).filter(Contact.source_id == source_id).all()

    def get_with_details(
        self, db: Session, *, contact_id: int
    ) -> Optional[Contact]:
        return db.query(Contact).filter(Contact.id == contact_id).first()

    def get_multi_with_details(self, db: Session, *, skip: int = 0,
        limit: int = 100, source_id: Optional[int] = None,
        operator_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[Contact]:
        query = db.query(Contact)
        if source_id:
            query = query.filter(Contact.source_id == source_id)
        if operator_id:
            query = query.filter(Contact.operator_id == operator_id)
        if is_active is not None:
            query = query.filter(Contact.is_active == is_active)
        return query.offset(skip).limit(limit).all()

    def get_stats_by_operator(self, db: Session) -> Dict:
        stats = db.query(
            Contact.operator_id,
            func.count(Contact.id).label('total_contacts'),
            func.sum(case((Contact.is_active == True, 1), else_=0))
            .label('active_contacts')
        ).group_by(Contact.operator_id).all()
        return {
            stat.operator_id: {
                'total_contacts': stat.total_contacts,
                'active_contacts': stat.active_contacts or 0
            }
            for stat in stats
        }

    def get_stats_by_source(self, db: Session) -> Dict:
        stats = db.query(
            Contact.source_id,
            func.count(Contact.id).label('total_contacts')
        ).group_by(Contact.source_id).all()

        return {
            stat.source_id: {
                'total_contacts': stat.total_contacts
            }
            for stat in stats
        }


contact = CRUDContact(Contact)
