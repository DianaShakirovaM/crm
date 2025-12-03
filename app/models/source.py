from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.session import Base


class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)

    operator_weights = relationship(
        'SourceOperatorWeight',
        back_populates='source',
        cascade="all, delete-orphan"
    )
    contacts = relationship('Contact', back_populates='source')


class SourceOperatorWeight(Base):
    __tablename__ = 'source_operator_weights'

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('sources.id'))
    operator_id = Column(Integer, ForeignKey('operators.id'))
    weight = Column(Integer, default=1)

    source = relationship('Source', back_populates='operator_weights')
    operator = relationship('Operator', back_populates='source_weights')
