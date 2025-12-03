from fastapi import APIRouter

from app.api.endpoints import (
    contact,
    lead,
    operator,
    source,
    stats,
)

api_router = APIRouter()

api_router.include_router(
    operator.router, prefix='/operators', tags=["operators"])
api_router.include_router(source.router, prefix='/sources', tags=["sources"])
api_router.include_router(
    contact.router, prefix='/contacts', tags=["contacts"])
api_router.include_router(lead.router, prefix='/leads', tags=["leads"])
api_router.include_router(stats.router, prefix='/stats', tags=["stats"])
