from sqlalchemy import Column, Integer, String, Sequence, DateTime, func, UniqueConstraint
from database.db import Base

class Comercializacao(Base):
    __tablename__ = 'comercializacao'
    __table_args__ = (
        UniqueConstraint('item', 'subitem', name='uix_comercializacao_item_subitem'),
    )

    id        = Column(Integer, Sequence('comercializacao_id_seq'), primary_key=True)
    item      = Column(String(100), nullable=False)
    subitem   = Column(String(100), nullable=False)
    quantidade= Column(Integer, nullable=True)
    created   = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated   = Column(DateTime(timezone=True), nullable=True)