from typing import Optional

from pydantic import BaseModel


class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class SourceUpdate(SourceBase):
    name: Optional[str] = None
    description: Optional[str] = None


class Source(SourceBase):
    id: int

    class Config:
        from_attributes = True


class SourceOperatorWeightBase(BaseModel):
    operator_id: int
    weight: int = 1


class SourceOperatorWeightCreate(SourceOperatorWeightBase):
    pass


class SourceOperatorWeight(SourceOperatorWeightBase):
    id: int
    source_id: int

    class Config:
        from_attributes = True
