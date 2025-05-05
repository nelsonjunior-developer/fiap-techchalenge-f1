# database/models/processamento.py

from sqlalchemy import Column, Integer, String, Sequence, DateTime, func, UniqueConstraint, Enum
from database.db import Base
import enum

class GrapeTypeEnum(str, enum.Enum):
    viniferas = "viniferas"
    uvas_de_mesa = "uvas_de_mesa"
    americanas_e_hibridas = "americanas_e_hibridas"

class Processamento(Base):
    __tablename__ = 'processamento'
    __table_args__ = (
        UniqueConstraint('category', 'variety', 'grape_type', name='uix_processamento_category_variety_type'),
    )

    id          = Column(Integer, Sequence('processamento_id_seq'), primary_key=True)
    category    = Column(String(100), nullable=False)
    variety     = Column(String(100), nullable=False)
    quantidade  = Column(Integer, nullable=True)
    grape_type  = Column(Enum(GrapeTypeEnum, name="grape_type_enum"), nullable=False)
    created     = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated     = Column(DateTime(timezone=True), nullable=True)