# captura/processor.py

import logging
from captura.scrapers.producao_scraper import get_item_subitems as get_producao_subitems
from captura.scrapers.commercializacao_scraper import get_item_subitems as get_commercializacao_subitems
from captura.scrapers.processamento_scraper import get_all_processamento_data
from captura.data_handler import normalize_quantity

from database.db import engine, Base
from database.repos.production_repo import save_producao_records
from database.repos.commercializacao_repo import save_commercializacao_records
from database.repos.processamento_repo import save_processamento_records
from database.repos.execution_repo import save_execution_status

from database.models.execution_status import ExecutionStatusEnum, ExecutionTabEnum
from database.models.processamento import GrapeTypeEnum

# Configura o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cria tabelas no banco (incluindo execution_status)
Base.metadata.create_all(bind=engine)


def process_and_save_producao():
    tab = ExecutionTabEnum.producao
    try:
        raw = get_producao_subitems()
        records = []
        for item, subitem, qty_str in raw:
            quantidade = normalize_quantity(qty_str)
            records.append({
                "item": item,
                "subitem": subitem,
                "quantidade": quantidade,
            })

        if records:
            save_producao_records(records)
            logger.info(f"{len(records)}### registros de processamento salvos com sucesso!!!")
            save_execution_status(status=ExecutionStatusEnum.success, tab=tab)
        else:
            msg = "Nenhum registro válido encontrado para produção."
            logger.warning(msg)
            save_execution_status(status=ExecutionStatusEnum.error, tab=tab, error_message=msg)

    except Exception as e:
        msg = str(e)
        logger.error(f"Erro no ETL de produção: {msg}")
        save_execution_status(status=ExecutionStatusEnum.error, tab=tab, error_message=msg)


def process_and_save_commercializacao():
    tab = ExecutionTabEnum.comercializacao
    try:
        raw = get_commercializacao_subitems()
        records = []
        for item, subitem, qty_str in raw:
            quantidade = normalize_quantity(qty_str)
            records.append({
                "item": item,
                "subitem": subitem,
                "quantidade": quantidade,
            })

        if records:
            save_commercializacao_records(records)
            logger.info(f"{len(records)}### registros de processamento salvos com sucesso!!!")
            save_execution_status(status=ExecutionStatusEnum.success, tab=tab)
        else:
            msg = "Nenhum registro válido encontrado para comercialização."
            logger.warning(msg)
            save_execution_status(status=ExecutionStatusEnum.error, tab=tab, error_message=msg)

    except Exception as e:
        msg = str(e)
        logger.error(f"Erro no ETL de comercialização: {msg}")
        save_execution_status(status=ExecutionStatusEnum.error, tab=tab, error_message=msg)


def process_and_save_processamento():
    tab = ExecutionTabEnum.processamento
    try:
        raw = get_all_processamento_data()
        records = []
        for category, variety, qty_str, grape_type_str in raw:
            quantidade = normalize_quantity(qty_str)

            try:
                grape_type_enum = GrapeTypeEnum(grape_type_str)
            except ValueError:
                logger.warning(f"Grape type inválido ignorado: {grape_type_str}")
                continue

            records.append({
                "category": category,
                "variety": variety,
                "quantidade": quantidade,
                "grape_type": grape_type_enum,
            })

        if records:
            save_processamento_records(records)
            logger.info(f"{len(records)}### registros de processamento salvos com sucesso!!!")
            save_execution_status(status=ExecutionStatusEnum.success, tab=tab)
        else:
            msg = "Nenhum registro válido encontrado para processamento."
            logger.warning(msg)
            save_execution_status(status=ExecutionStatusEnum.error, tab=tab, error_message=msg)

    except Exception as e:
        msg = str(e)
        logger.error(f"Erro no ETL de processamento: {msg}")
        save_execution_status(status=ExecutionStatusEnum.error, tab=tab, error_message=msg)


if __name__ == "__main__":
    logger.info("Iniciando processamento completo da API FIAP...")

    try:
        process_and_save_commercializacao()
    except Exception:
        logger.exception("Falha crítica em comercialização.")

    try:
        process_and_save_producao()
    except Exception:
        logger.exception("Falha crítica em produção.")

    try:
        process_and_save_processamento()
    except Exception:
        logger.exception("Falha crítica em processamento.")