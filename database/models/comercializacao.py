from sqlalchemy import Column, Integer, String, Sequence, DateTime, func, UniqueConstraint
from database.db import Base

class Comercializacao(Base):
    __tablename__ = 'comercializacao'
    __table_args__ = (
        UniqueConstraint('item', 'subitem', 'ano', name='uix_comercializacao_item_subitem_ano'),
    )

    id          = Column(Integer, Sequence('comercializacao_id_seq'), primary_key=True)
    item        = Column(String(100), nullable=False)
    subitem     = Column(String(100), nullable=False)
    quantidade  = Column(Integer, nullable=True)
    ano         = Column(Integer, nullable=False, doc="Ano da comercialização")

    created     = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated     = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)