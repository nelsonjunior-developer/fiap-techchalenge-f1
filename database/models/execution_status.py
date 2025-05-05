# database/models/execution_status.py

import enum
from sqlalchemy import Column, Integer, Enum, String, DateTime, func
from database.db import Base

class ExecutionStatusEnum(str, enum.Enum):
    success = 'success'
    error   = 'error'

class ExecutionTabEnum(str, enum.Enum):
    producao        = 'producao'
    processamento   = 'processamento'
    comercializacao = 'comercializacao'
    importacao      = 'importacao'
    exportacao      = 'exportacao'

class ExecutionStatus(Base):
    __tablename__ = 'execution_status'

    id            = Column(Integer, primary_key=True, autoincrement=True)
    status        = Column(Enum(ExecutionStatusEnum, name='exec_status_enum'), nullable=False)
    tab           = Column(Enum(ExecutionTabEnum,   name='exec_tab_enum'),    nullable=False)
    error_message = Column(String, nullable=True)
    created       = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc='Timestamp when this execution record was created'
    )