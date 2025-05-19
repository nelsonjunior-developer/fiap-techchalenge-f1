import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from database.db import SessionLocal
from database.models.producao import Producao

logger = logging.getLogger(__name__)

def save_producao_records(records: list[dict]) -> None:
    """
    Upsert em lote dos registros da tabela 'producao',
    usando a combinação (item, subitem, ano) como chave única.
    """
    session = SessionLocal()
    logger.info(f"Iniciando upsert de {len(records)} registros de produção...")

    stmt = insert(Producao).values(records)

    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=['item', 'subitem', 'ano'],
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
        logger.error(f"Erro ao realizar upsert na tabela producao: {e}")
        raise
    finally:
        session.close()