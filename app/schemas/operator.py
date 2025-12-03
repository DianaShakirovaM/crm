from typing import Optional

from pydantic import BaseModel


class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    max_load: int = 10


class OperatorCreate(OperatorBase):
    pass


class OperatorUpdate(OperatorBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    max_load: Optional[int] = None


class Operator(OperatorBase):
    id: int
    current_load: Optional[int] = 0

    class Config:
        from_attributes = True


class OperatorActivate(BaseModel):
    active: bool


class OperatorLoadLimit(BaseModel):
    max_load: int
