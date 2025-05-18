# database/models/exportacao.py

from sqlalchemy import Column, Integer, String, Float, DateTime, func, UniqueConstraint
from database.db import Base

class Exportacao(Base):
    __tablename__ = "exportacao"
    __table_args__ = (
        UniqueConstraint("categoria", "pais", "ano", name="uq_exportacao_categoria_pais_ano"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    categoria = Column(String, nullable=False)  # Ex: vinhos_de_mesa, espumantes, etc.
    pais = Column(String, nullable=False)
    ano = Column(Integer, nullable=False)
    quantidade_kg = Column(Float, nullable=True)
    valor_usd = Column(Float, nullable=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())