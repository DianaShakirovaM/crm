from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.contact import contact as contact_crud
from app.crud.operator import operator as operator_crud
from app.database.session import get_db
from app.schemas.operator import (
    Operator,
    OperatorActivate,
    OperatorCreate,
    OperatorLoadLimit,
    OperatorUpdate,
)


router = APIRouter()


@router.post('/', response_model=Operator, status_code=201)
def create_operator(
    operator_in: OperatorCreate,
    db: Session = Depends(get_db)
):
    return operator_crud.create(db, obj_in=operator_in)


@router.get('/', response_model=List[Operator])
def read_operators(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return operator_crud.get_multi_with_load(db, skip=skip, limit=limit)


@router.get('/{operator_id}', response_model=Operator)
def read_operator(
    operator_id: int,
    db: Session = Depends(get_db)
):
    db_operator = operator_crud.get_with_load(db, operator_id=operator_id)
    if not db_operator:
        raise HTTPException(status_code=404, detail='Operator not found')
    return db_operator


@router.put('/{operator_id}', response_model=Operator)
def update_operator(
    operator_id: int,
    operator_in: OperatorUpdate,
    db: Session = Depends(get_db)
):
    db_operator = operator_crud.get(db, id=operator_id)
    if not db_operator:
        raise HTTPException(status_code=404, detail='Operator not found')
    return operator_crud.update(db, db_obj=db_operator, obj_in=operator_in)


@router.patch('/{operator_id}/activate')
def activate_operator(
    operator_id: int,
    activate_data: OperatorActivate,
    db: Session = Depends(get_db)
):
    db_operator = operator_crud.get(db, id=operator_id)
    if not db_operator:
        raise HTTPException(status_code=404, detail='Operator not found')

    operator_crud.update(
        db, db_obj=db_operator, obj_in={'is_active': activate_data.active})

    status = 'activated' if activate_data.active else 'deactivated'
    return {'message': f'Operator {status}'}


@router.patch('/{operator_id}/load-limit')
def set_load_limit(
    operator_id: int,
    load_data: OperatorLoadLimit,
    db: Session = Depends(get_db)
):
    db_operator = operator_crud.get(db, id=operator_id)
    if not db_operator:
        raise HTTPException(status_code=404, detail='Operator not found')

    operator_crud.update(
        db, db_obj=db_operator, obj_in={'max_load': load_data.max_load})

    return {'message': 'Load limit set to {load_data.max_load}'}


@router.get('/{operator_id}/stats')
def get_operator_stats(
    operator_id: int,
    db: Session = Depends(get_db)
):
    db_operator = operator_crud.get_with_load(db, operator_id=operator_id)
    if not db_operator:
        raise HTTPException(status_code=404, detail='Operator not found')

    contacts = contact_crud.get_by_operator_id(db, operator_id=operator_id)

    from collections import defaultdict
    source_stats = defaultdict(int)
    for contact in contacts:
        source_stats[contact.source_id] += 1

    from app.models.source import Source
    source_details = []
    for source_id, count in source_stats.items():
        source = db.query(Source).filter(Source.id == source_id).first()
        if source:
            source_details.append({
                'source_id': source_id,
                'source_name': source.name,
                'count': count
            })

    return {
        'operator': {
            'id': db_operator.id,
            'name': db_operator.name,
            'is_active': db_operator.is_active,
            'max_load': db_operator.max_load,
            'current_load': db_operator.current_load
        },
        'contacts_total': len(contacts),
        'contacts_active': len([c for c in contacts if c.is_active]),
        'by_source': source_details
    }


@router.delete('/{operator_id}')
def delete_operator(
    operator_id: int,
    db: Session = Depends(get_db)
):
    db_operator = operator_crud.get(db, id=operator_id)
    if not db_operator:
        raise HTTPException(status_code=404, detail='Operator not found')

    operator_crud.remove(db, id=operator_id)
    return {'message': 'Operator deleted successfully'}
