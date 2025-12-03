from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    status = Column(String, default='new')
    operator_id = Column(Integer, ForeignKey('operators.id'))
    message = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship('Lead', back_populates='contacts')
    source = relationship('Source', back_populates='contacts')
    operator = relationship('Operator', back_populates='contacts')
