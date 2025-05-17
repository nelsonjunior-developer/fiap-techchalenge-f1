# database/models/execution_status.py

import enum
from sqlalchemy import Column, Integer, Enum, String, DateTime, func
from database.db import Base

class ExecutionStatusEnum(str, enum.Enum):
    success = 'success'
    error   = 'error'

class ExecutionTabEnum(str, enum.Enum):
    producao                      = 'producao'
    processamento                 = 'processamento'
    comercializacao               = 'comercializacao'
    importacao                    = 'importacao'

    # Seções da aba Exportação
    exportacao_tab_subopt_01     = 'exportacao_tab_subopt_01'  # vinhos de mesa
    exportacao_tab_subopt_02     = 'exportacao_tab_subopt_02'  # espumantes
    exportacao_tab_subopt_03     = 'exportacao_tab_subopt_03'  # uvas frescas
    exportacao_tab_subopt_04     = 'exportacao_tab_subopt_04'  # suco de uva

     # 🆕 IMPORTAÇÃO
    importacao_tab_subopt_01 = "importacao_tab_subopt_01"
    importacao_tab_subopt_02 = "importacao_tab_subopt_02"
    importacao_tab_subopt_03 = "importacao_tab_subopt_03"
    importacao_tab_subopt_04 = "importacao_tab_subopt_04"
    importacao_tab_subopt_05 = "importacao_tab_subopt_05"

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