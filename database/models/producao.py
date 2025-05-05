from sqlalchemy import Column, Integer, String, Sequence, DateTime, func, UniqueConstraint
from database.db import Base

class Producao(Base):
    __tablename__ = 'producao'
    __table_args__ = (
        UniqueConstraint('item', 'subitem', name='uix_item_subitem'),
    )

    id        = Column(Integer, Sequence('producao_id_seq'), primary_key=True)
    item      = Column(String(100), nullable=False)
    subitem   = Column(String(100), nullable=False)
    quantidade= Column(Integer, nullable=True)

    # set once when first inserted
    created   = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when this record was first created"
    )
    # set on every UPDATE
    updated   = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when this record was last updated"
    )