from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.session import Base


class Operator(Base):
    __tablename__ = 'operators'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    max_load = Column(Integer, default=10)

    source_weights = relationship(
        'SourceOperatorWeight', back_populates='operator')
    contacts = relationship('Contact', back_populates='operator')
