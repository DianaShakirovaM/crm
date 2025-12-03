from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class Lead(Base):
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contacts = relationship('Contact', back_populates='lead')
