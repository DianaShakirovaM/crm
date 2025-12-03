from typing import List, Dict

from pydantic import BaseModel


class OperatorStats(BaseModel):
    operator_id: int
    operator_name: str
    total_contacts: int
    active_contacts: int
    load_percentage: float
    max_load: int


class SourceStats(BaseModel):
    source_id: int
    source_name: str
    total_contacts: int


class DistributionStats(BaseModel):
    by_operator: List[OperatorStats]
    by_source: List[SourceStats]
    summary: Dict[str, int]
