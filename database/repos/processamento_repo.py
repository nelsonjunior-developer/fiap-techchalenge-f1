# database/repos/processamento_repo.py

import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from database.db import SessionLocal
from database.models.processamento import Processamento

logger = logging.getLogger(__name__)

def save_processamento_records(records: list[dict]) -> None:
    """
    Realiza upsert (inserção ou atualização) em lote para os registros da tabela processamento.
    Considera como chave única a combinação (category, variety, grape_type).
    """
    session = SessionLocal()
    logger.info(f"Iniciando upsert de {len(records)} registros de processamento...")

    stmt = insert(Processamento).values(records)

    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=['category', 'variety', 'grape_type'],
        set_={
            'quantidade': stmt.excluded.quantidade,
            'updated': func.now()
        }
    )

    try:
        result = session.execute(upsert_stmt)
        session.commit()
        logger.info(f"Upsert concluído. Linhas afetadas: {getattr(result, 'rowcount', 'desconhecido')}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Erro ao realizar upsert na tabela processamento: {e}")
        raise
    finally:
        session.close()