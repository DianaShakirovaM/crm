from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.crud.contact import contact as contact_crud
from app.database.session import get_db
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.operator import Operator
from app.models.source import Source
from app.schemas.stats import DistributionStats

router = APIRouter()


@router.get('/distribution', response_model=DistributionStats)
def get_distribution_stats(
    db: Session = Depends(get_db)
):
    operators = db.query(Operator).all()
    operator_stats = []

    contact_stats = contact_crud.get_stats_by_operator(db)

    for operator in operators:
        stats = contact_stats.get(
            operator.id, {'total_contacts': 0, 'active_contacts': 0})
        load_percentage = (
            (stats['active_contacts'] / operator.max_load * 100)
            if operator.max_load > 0 else 0)

        operator_stats.append({
            'operator_id': operator.id,
            'operator_name': operator.name,
            'total_contacts': stats['total_contacts'],
            'active_contacts': stats['active_contacts'],
            'load_percentage': round(load_percentage, 2),
            'max_load': operator.max_load
        })

    sources = db.query(Source).all()
    source_stats = []

    source_contact_stats = contact_crud.get_stats_by_source(db)

    for source in sources:
        stats = source_contact_stats.get(source.id, {'total_contacts': 0})

        source_stats.append({
            'source_id': source.id,
            'source_name': source.name,
            'total_contacts': stats['total_contacts']
        })

    total_leads = db.query(func.count(Lead.id)).scalar()
    total_contacts = db.query(func.count(Contact.id)).scalar()
    active_contacts = db.query(func.count(Contact.id)).filter(
        Contact.is_active == True).scalar()
    operators_online = db.query(func.count(Operator.id)).filter(
        Operator.is_active == True
    ).scalar()
    operators_total = db.query(func.count(Operator.id)).scalar()

    return {
        'by_operator': operator_stats,
        'by_source': source_stats,
        'summary': {
            'total_leads': total_leads or 0,
            'total_contacts': total_contacts or 0,
            'active_contacts': active_contacts or 0,
            'operators_online': operators_online or 0,
            'operators_total': operators_total or 0
        }
    }
