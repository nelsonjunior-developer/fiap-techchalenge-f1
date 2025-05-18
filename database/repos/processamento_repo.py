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
    Considera como chave única a combinação (category, variety, grape_type, ano).
    """
    session = SessionLocal()
    logger.info(f"Iniciando upsert de {len(records)} registros de processamento...")

    cleaned_records = []
    for rec in records:
        required_fields = ["category", "variety", "quantidade", "grape_type", "ano"]
        if all(field in rec for field in required_fields):
            cleaned_records.append(rec)
        else:
            logger.warning(f"Registro descartado por campos ausentes: {rec}")

    if not cleaned_records:
        logger.warning("Nenhum registro válido para inserir na tabela processamento.")
        return

    stmt = insert(Processamento).values(cleaned_records)

    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=["category", "variety", "grape_type", "ano"],
        set_={
            "quantidade": stmt.excluded.quantidade,
            "updated": func.now()
        }
    )

    try:
        result = session.execute(upsert_stmt)
        session.commit()
        logger.info(f"Upsert concluído. Linhas afetadas: {getattr(result, 'rowcount', None)}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Erro ao realizar upsert na tabela processamento: {e}")
        raise
    finally:
        session.close()