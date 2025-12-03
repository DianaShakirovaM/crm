from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud.contact import contact as contact_crud
from app.crud.lead import lead as lead_crud
from app.crud.operator import operator as operator_crud
from app.crud.source import source as source_crud
from app.database.session import get_db
from app.models.contact import Contact as ContactModel
from app.models.source import Source as SourceModel
from app.schemas.contact import ContactCreate, ContactStatusUpdate
from app.schemas.response import ContactWithDetails
from app.services.distribution import DistributionService


router = APIRouter()
distribution_service = DistributionService()


@router.post('/', response_model=ContactWithDetails, status_code=201)
def create_contact(
    contact_in: ContactCreate,
    db: Session = Depends(get_db)
):
    lead = lead_crud.get_or_create(
        db,
        external_id=contact_in.lead_external_id,
        email=contact_in.lead_email,
        phone=contact_in.lead_phone
    )

    source = db.query(SourceModel).filter(
        SourceModel.id == contact_in.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail='Source not found')

    distribution_result = distribution_service.distribute(
        db, source_id=contact_in.source_id)

    operator_id = None
    # ФИКС: проверяем, что distribution_result не равен None
    if distribution_result and distribution_result.operator:
        operator_id = distribution_result.operator.id

    db_contact = ContactModel(
        lead_id=lead.id,
        source_id=contact_in.source_id,
        operator_id=operator_id,
        message=contact_in.message,
        is_active=True
    )

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    contact = contact_crud.get_with_details(db, contact_id=db_contact.id)
    lead_obj = lead_crud.get(db, id=lead.id)
    source_obj = source_crud.get(db, id=contact_in.source_id)
    operator_obj = None
    if operator_id:
        operator_obj = operator_crud.get(db, id=operator_id)

    return {
        'id': contact.id,
        'lead_external_id': contact_in.lead_external_id,
        'source_id': contact_in.source_id,
        'message': contact_in.message,
        'lead_email': contact_in.lead_email,
        'lead_phone': contact_in.lead_phone,
        'lead_id': lead.id,
        'operator_id': operator_id,
        'is_active': contact.is_active,
        'created_at': contact.created_at,
        'lead': lead_obj,
        'source': source_obj,
        'operator': operator_obj
    }


@router.get('/', response_model=List[ContactWithDetails])
def read_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source_id: Optional[int] = None,
    operator_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    contacts = contact_crud.get_multi_with_details(
        db,
        skip=skip,
        limit=limit,
        source_id=source_id,
        operator_id=operator_id,
        is_active=is_active
    )

    result = []
    for contact in contacts:
        lead = lead_crud.get(db, id=contact.lead_id)
        source = source_crud.get(db, id=contact.source_id)
        operator = None
        if contact.operator_id:
            operator = operator_crud.get(db, id=contact.operator_id)

        contact_data = {
            'id': contact.id,
            'lead_external_id': lead.external_id if lead else "",
            'source_id': contact.source_id,
            'message': contact.message,
            'lead_email': lead.email if lead else None,
            'lead_phone': lead.phone if lead else None,
            'lead_id': contact.lead_id,
            'operator_id': contact.operator_id,
            'is_active': contact.is_active,
            'created_at': contact.created_at,
            'lead': lead,
            'source': source,
            'operator': operator
        }
        result.append(contact_data)

    return result


@router.patch('/{contact_id}/status')
def update_contact_status(
    contact_id: int,
    status_data: ContactStatusUpdate,
    db: Session = Depends(get_db)
):
    """Обновление статуса контакта (активен/не активен)"""
    contact = contact_crud.get(db, id=contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail='Contact not found')
    contact_crud.update(
        db, db_obj=contact, obj_in={"is_active": status_data.is_active})
    return {
        'message':
        "Contact status updated to "
        f"{'active' if status_data.is_active else 'inactive'}"}


@router.get('/{contact_id}', response_model=ContactWithDetails)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):
    contact = contact_crud.get_with_details(db, contact_id=contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail='Contact not found')
    lead = lead_crud.get(db, id=contact.lead_id)
    source = source_crud.get(db, id=contact.source_id)
    operator = None
    if contact.operator_id:
        operator = operator_crud.get(db, id=contact.operator_id)

    return {
        'id': contact.id,
        'lead_external_id': lead.external_id if lead else "",
        'source_id': contact.source_id,
        'message': contact.message,
        'lead_email': lead.email if lead else None,
        'lead_phone': lead.phone if lead else None,
        'lead_id': contact.lead_id,
        'operator_id': contact.operator_id,
        'is_active': contact.is_active,
        'created_at': contact.created_at,
        'lead': lead,
        'source': source,
        'operator': operator
    }
