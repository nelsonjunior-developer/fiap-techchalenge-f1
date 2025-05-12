# database/models/exportacao.py

from sqlalchemy import Column, Integer, String, Sequence, DateTime, func, UniqueConstraint
from sqlalchemy.types import Numeric
from database.db import Base

class Exportacao(Base):
    __tablename__ = 'exportacao'
    __table_args__ = (
        UniqueConstraint('categoria', 'pais', name='uix_exportacao_categoria_pais'),
    )

    id            = Column(Integer, Sequence('exportacao_id_seq'), primary_key=True)
    categoria     = Column(String(50), nullable=False, doc="Seção da aba: vinhos_de_mesa, espumantes, uvas_frescas, suco_de_uva")
    pais          = Column(String(100), nullable=False)
    quantidade_kg = Column(Integer, nullable=True, doc="Quantidade exportada em KG")
    valor_usd     = Column(Numeric(precision=12, scale=2), nullable=True, doc="Valor exportado em dólares")
    created       = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated       = Column(DateTime(timezone=True), nullable=True)