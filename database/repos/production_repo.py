# database/production_repo.py

import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from database.db import SessionLocal
from database.models.producao import Producao


logger = logging.getLogger(__name__)

def save_producao_records(records: list[dict]) -> None:
    """
    Upsert a batch of records into producao,
    matching on the unique (item, subitem) constraint.
    'created' stays at its original timestamp,
    'updated' is set to now() on every update.
    """
    session = SessionLocal()
    logger.info(f"Iniciando upsert de {len(records)} registros de produção...")

    stmt = insert(Producao).values(records)
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=['item', 'subitem'],
        set_={
            # update quantity
            'quantidade': stmt.excluded.quantidade,
            # set updated on each conflict
            'updated': func.now()
        }
    )

    try:
        result = session.execute(upsert_stmt)
        session.commit()
        rowcount = getattr(result, 'rowcount', None)
        logger.info(f"Upsert concluído. Linhas afetadas: {rowcount}.")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Erro ao realizar upsert na tabela producao: {e}")
        raise
    finally:
        session.close()