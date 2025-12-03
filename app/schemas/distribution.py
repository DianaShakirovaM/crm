from typing import List, Optional

from pydantic import BaseModel

from app.schemas.operator import Operator


class DistributionResult(BaseModel):
    success: bool
    operator: Optional[Operator] = None
    alternatives: List[Operator] = []
    error: Optional[str] = None


class DistributionConfig(BaseModel):
    strategy: str = 'weighted_random'
    fallback_enabled: bool = True
    notify_on_failure: bool = False
