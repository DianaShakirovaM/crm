from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud.contact import contact as contact_crud
from app.crud.lead import lead as lead_crud
from app.database.session import get_db
from app.models.operator import Operator as OperatorModel
from app.models.source import Source as SourceModel
from app.schemas.lead import Lead
from app.schemas.response import ContactWithDetails, LeadWithContacts

router = APIRouter()


@router.get('/', response_model=List[Lead])
def read_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return lead_crud.get_multi_with_contact_count(db, skip=skip, limit=limit)


@router.get('/{lead_id}', response_model=LeadWithContacts)
def read_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    lead = lead_crud.get_with_contact_count(db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail='Lead not found')
    contacts = contact_crud.get_by_lead_id(db, lead_id=lead_id)
    enriched_contacts = []
    for contact in contacts:
        source = db.query(SourceModel).filter(
            SourceModel.id == contact.source_id).first()
        operator = None
        if contact.operator_id:
            operator = db.query(OperatorModel).filter(
                OperatorModel.id == contact.operator_id).first()
        contact_data = {
            'id': contact.id,
            'lead_external_id': lead.external_id,
            'source_id': contact.source_id,
            'message': contact.message,
            'lead_email': lead.email,
            'lead_phone': lead.phone,
            'lead_id': contact.lead_id,
            'operator_id': contact.operator_id,
            'is_active': contact.is_active,
            'created_at': contact.created_at,
            'lead': lead,
            'source': source,
            'operator': operator
        }
        enriched_contacts.append(contact_data)

    return {
        'id': lead.id,
        'external_id': lead.external_id,
        'email': lead.email,
        'phone': lead.phone,
        'created_at': lead.created_at,
        'contact_count': lead.contact_count,
        'contacts': enriched_contacts
    }


@router.get('/by-external/{external_id}', response_model=LeadWithContacts)
def read_lead_by_external_id(
    external_id: str,
    db: Session = Depends(get_db)
):
    lead = lead_crud.get_by_external_id(db, external_id=external_id)
    if not lead:
        raise HTTPException(status_code=404, detail='Lead not found')

    lead_with_count = lead_crud.get_with_contact_count(db, lead_id=lead.id)

    contacts = contact_crud.get_by_lead_id(db, lead_id=lead.id)

    enriched_contacts = []
    for contact in contacts:
        source = db.query(SourceModel).filter(
            SourceModel.id == contact.source_id).first()
        operator = None
        if contact.operator_id:
            operator = db.query(OperatorModel).filter(
                OperatorModel.id == contact.operator_id).first()

        contact_data = {
            'id': contact.id,
            'lead_external_id': lead.external_id,
            'source_id': contact.source_id,
            'message': contact.message,
            'lead_email': lead.email,
            'lead_phone': lead.phone,
            'lead_id': contact.lead_id,
            'operator_id': contact.operator_id,
            'is_active': contact.is_active,
            'created_at': contact.created_at,
            'lead': lead_with_count,
            'source': source,
            'operator': operator
        }
        enriched_contacts.append(contact_data)

    return {
        'id': lead.id,
        'external_id': lead.external_id,
        'email': lead.email,
        'phone': lead.phone,
        'created_at': lead.created_at,
        'contact_count': lead_with_count.contact_count,
        'contacts': enriched_contacts
    }


@router.get('/{lead_id}/contacts', response_model=List[ContactWithDetails])
def get_lead_contacts(
    lead_id: int,
    db: Session = Depends(get_db)
):
    lead = lead_crud.get(db, id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    contacts = contact_crud.get_by_lead_id(db, lead_id=lead_id)

    result = []
    for contact in contacts:
        source = db.query(SourceModel).filter(
            SourceModel.id == contact.source_id).first()
        operator = None
        if contact.operator_id:
            operator = db.query(OperatorModel).filter(
                OperatorModel.id == contact.operator_id).first()

        contact_data = {
            'id': contact.id,
            'lead_external_id': lead.external_id,
            'source_id': contact.source_id,
            'message': contact.message,
            'lead_email': lead.email,
            'lead_phone': lead.phone,
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
