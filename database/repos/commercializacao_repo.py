import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from database.db import SessionLocal
from database.models.comercializacao import Comercializacao

logger = logging.getLogger(__name__)

def save_commercializacao_records(records: list[dict]) -> None:
    session = SessionLocal()
    logger.info(f"Iniciando upsert de {len(records)} registros de comercialização...")

    stmt = insert(Comercializacao).values(records)
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=['item', 'subitem'],
        set_={
            'quantidade': stmt.excluded.quantidade,
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
        logger.error(f"Erro ao fazer upsert na tabela comercialização: {e}")
        raise
    finally:
        session.close()