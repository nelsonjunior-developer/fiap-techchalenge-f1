# database/repos/exportacao_repo.py

import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from database.db import SessionLocal
from database.models.exportacao import Exportacao

logger = logging.getLogger(__name__)

def _save_exportacao(records: list[dict], categoria: str) -> None:
    session = SessionLocal()
    logger.info(f"Iniciando upsert de {len(records)} registros de exportação para categoria '{categoria}'...")

    for rec in records:
        rec['categoria'] = categoria

    stmt = insert(Exportacao).values(records)
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=['categoria', 'pais'],
        set_={
            'quantidade_kg': stmt.excluded.quantidade_kg,
            'valor_usd': stmt.excluded.valor_usd,
            'updated': func.now()
        }
    )

    try:
        result = session.execute(upsert_stmt)
        session.commit()
        logger.info(f"Upsert concluído. Linhas afetadas: {getattr(result, 'rowcount', None)}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Erro ao realizar upsert na tabela exportacao: {e}")
        raise
    finally:
        session.close()

# Wrappers para cada aba de exportação
def save_exportacao_vinhos_de_mesa(records: list[dict]) -> None:
    _save_exportacao(records, categoria="vinhos_de_mesa")

def save_exportacao_espumantes(records: list[dict]) -> None:
    _save_exportacao(records, categoria="espumantes")

def save_exportacao_uvas_frescas(records: list[dict]) -> None:
    _save_exportacao(records, categoria="uvas_frescas")

def save_exportacao_suco_uva(records: list[dict]) -> None:
    _save_exportacao(records, categoria="suco_de_uva")