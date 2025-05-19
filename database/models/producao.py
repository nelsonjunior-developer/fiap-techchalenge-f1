from sqlalchemy import Column, Integer, String, Sequence, DateTime, func, UniqueConstraint
from database.db import Base

class Producao(Base):
    __tablename__ = 'producao'
    __table_args__ = (
        UniqueConstraint('item', 'subitem', 'ano', name='uix_producao_item_subitem_ano'),
    )

    id         = Column(Integer, Sequence('producao_id_seq'), primary_key=True)
    item       = Column(String(100), nullable=False)
    subitem    = Column(String(100), nullable=False)
    quantidade = Column(Integer, nullable=True)
    ano        = Column(Integer, nullable=False, doc="Ano da produção")

    created    = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp de criação"
    )
    updated    = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
        doc="Timestamp de última atualização"
    )