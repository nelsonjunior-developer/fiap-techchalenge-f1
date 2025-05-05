# database/execution_repo.py

import logging
from sqlalchemy.exc import SQLAlchemyError
from database.db import SessionLocal
from database.models.execution_status import (
    ExecutionStatus,
    ExecutionStatusEnum,
    ExecutionTabEnum,
)

logger = logging.getLogger(__name__)

def save_execution_status(
    status: ExecutionStatusEnum,
    tab: ExecutionTabEnum,
    error_message: str = None
) -> None:
    """
    Insere um registro de status de execução.
      - status: success | error
      - tab: qual aba/processo (producao, processamento, etc.)
      - error_message: só para status=error
    """
    session = SessionLocal()
    try:
        record = ExecutionStatus(
            status=status,
            tab=tab,
            error_message=(error_message if status == ExecutionStatusEnum.error else None)
        )
        session.add(record)
        session.commit()
        logger.info(f"ExecutionStatus gravado: {status.value} on {tab.value}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Não foi possível gravar ExecutionStatus: {e}")
        raise
    finally:
        session.close()