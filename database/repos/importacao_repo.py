import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from database.db import SessionLocal
from database.models.importacao import Importacao

logger = logging.getLogger(__name__)


def _save_importacao(records: list[dict], categoria: str) -> None:
    session = SessionLocal()
    logger.info(f"Iniciando upsert de {len(records)} registros de importação para categoria '{categoria}'...")

    for rec in records:
        rec['categoria'] = categoria

    stmt = insert(Importacao).values(records)
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
        logger.error(f"Erro ao realizar upsert na tabela importacao: {e}")
        raise
    finally:
        session.close()


# Wrappers para cada aba de importação
def save_importacao_vinhos_de_mesa(records: list[dict]) -> None:
    _save_importacao(records, categoria="vinhos_de_mesa")

def save_importacao_espumantes(records: list[dict]) -> None:
    _save_importacao(records, categoria="espumantes")

def save_importacao_uvas_frescas(records: list[dict]) -> None:
    _save_importacao(records, categoria="uvas_frescas")

def save_importacao_uvas_passas(records: list[dict]) -> None:
    _save_importacao(records, categoria="uvas_passas")

def save_importacao_suco_uva(records: list[dict]) -> None:
    _save_importacao(records, categoria="suco_de_uva")