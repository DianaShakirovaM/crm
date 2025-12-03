from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate


class CRUDSource(CRUDBase[Source, SourceCreate, SourceUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Source]:
        return db.query(Source).filter(Source.name == name).first()

    def get_with_weights(
        self, db: Session, source_id: int
    ) -> Optional[Source]:
        return db.query(Source).filter(Source.id == source_id).first()


source = CRUDSource(Source)
