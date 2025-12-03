from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.contact import Contact
from app.models.operator import Operator
from app.schemas.operator import OperatorCreate, OperatorUpdate


class CRUDOperator(CRUDBase[Operator, OperatorCreate, OperatorUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Operator]:
        return db.query(Operator).filter(Operator.name == name).first()

    def get_active_operators(self, db: Session) -> List[Operator]:
        return db.query(Operator).filter(Operator.is_active == True).all()

    def get_with_load(
        self, db: Session, *, operator_id: int
    ) -> Optional[Operator]:
        operator = self.get(db, id=operator_id)
        if operator:
            current_load = db.query(func.count(Contact.id)).filter(
                Contact.operator_id == operator.id,
                Contact.is_active == True
            ).scalar()
            setattr(operator, 'current_load', current_load)
        return operator

    def get_multi_with_load(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Operator]:
        operators = self.get_multi(db, skip=skip, limit=limit)
        for operator in operators:
            current_load = db.query(func.count(Contact.id)).filter(
                Contact.operator_id == operator.id,
                Contact.is_active == True
            ).scalar()
            setattr(operator, 'current_load', current_load)
        return operators

    def update_load(
        self, db: Session, *, db_obj: Operator, load_change: int
    ) -> Operator:
        return self.update(
            db, db_obj=db_obj,
            obj_in={'cached_load': db_obj.cached_load + load_change})


operator = CRUDOperator(Operator)
