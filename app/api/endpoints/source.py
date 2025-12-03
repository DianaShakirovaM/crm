from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.source import source as source_crud
from app.database.session import get_db
from app.models.operator import Operator
from app.models.source import SourceOperatorWeight as WeightModel
from app.schemas.response import SourceWithWeights
from app.schemas.source import (
    Source,
    SourceCreate,
    SourceOperatorWeight,
    SourceOperatorWeightCreate,
)

router = APIRouter()


@router.post('/', response_model=Source, status_code=201)
def create_source(
    source_in: SourceCreate,
    db: Session = Depends(get_db)
):
    return source_crud.create(db, obj_in=source_in)


@router.get('/', response_model=List[Source])
def read_sources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return source_crud.get_multi(db, skip=skip, limit=limit)


@router.get('/{source_id}', response_model=SourceWithWeights)
def read_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    source = source_crud.get(db, id=source_id)
    if not source:
        raise HTTPException(status_code=404, detail='Source not found')

    weights = db.query(WeightModel).filter(
        WeightModel.source_id == source_id).all()

    result_weights = []
    for weight in weights:
        operator = db.query(Operator).filter(
            Operator.id == weight.operator_id).first()
        weight_dict = {
            'id': weight.id,
            'source_id': weight.source_id,
            'operator_id': weight.operator_id,
            'weight': weight.weight,
            'operator': operator
        }
        result_weights.append(weight_dict)

    source_dict = {
        'id': source.id,
        'name': source.name,
        'description': source.description,
        'operator_weights': result_weights
    }

    return source_dict


@router.post(
    '/{source_id}/weights/', response_model=List[SourceOperatorWeight])
def set_source_weights(
    source_id: int,
    weights: List[SourceOperatorWeightCreate],
    db: Session = Depends(get_db)
):
    source = source_crud.get(db, id=source_id)
    if not source:
        raise HTTPException(status_code=404, detail='Source not found')

    for weight in weights:
        operator = db.query(Operator).filter(
            Operator.id == weight.operator_id).first()
        if not operator:
            raise HTTPException(
                status_code=404,
                detail=f'Operator with id {weight.operator_id} not found'
            )

    db.query(WeightModel).filter(WeightModel.source_id == source_id).delete()

    result = []
    for weight in weights:
        db_weight = WeightModel(
            source_id=source_id,
            operator_id=weight.operator_id,
            weight=weight.weight
        )
        db.add(db_weight)
        result.append(db_weight)

    db.commit()

    for i, weight in enumerate(result):
        db.refresh(result[i])
        result[i].operator = db.query(Operator).filter(
            Operator.id == weight.operator_id).first()

    return result


@router.get('/{source_id}/weights/', response_model=List[SourceOperatorWeight])
def get_source_weights(
    source_id: int,
    db: Session = Depends(get_db)
):
    weights = db.query(WeightModel).filter(
        WeightModel.source_id == source_id).all()

    result = []
    for weight in weights:
        operator = db.query(Operator).filter(
            Operator.id == weight.operator_id).first()
        weight_dict = {
            'id': weight.id,
            'source_id': weight.source_id,
            'operator_id': weight.operator_id,
            'weight': weight.weight,
            'operator': operator
        }
        result.append(weight_dict)

    return result
