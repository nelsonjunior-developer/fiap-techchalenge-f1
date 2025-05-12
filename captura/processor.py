# captura/processor.py

import logging
from captura.scrapers.producao_scraper import get_item_subitems as get_producao_subitems
from captura.scrapers.commercializacao_scraper import get_item_subitems as get_commercializacao_subitems
from captura.scrapers.processamento_scraper import get_all_processamento_data
from captura.scrapers.exportacao_scraper import get_exportacao_data_by_section
from captura.data_handler import normalize_quantity

from database.db import engine, Base
from database.repos.production_repo import save_producao_records
from database.repos.commercializacao_repo import save_commercializacao_records
from database.repos.processamento_repo import save_processamento_records
from database.repos.exportacao_repo import (
    save_exportacao_vinhos_de_mesa,
    save_exportacao_espumantes,
    save_exportacao_uvas_frescas,
    save_exportacao_suco_uva
)
from database.repos.execution_repo import save_execution_status
from database.models.execution_status import ExecutionStatusEnum, ExecutionTabEnum
from database.models.processamento import GrapeTypeEnum

# Configura o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Garante que as tabelas existam
Base.metadata.create_all(bind=engine)


def process_and_save_producao():
    tab = ExecutionTabEnum.producao
    try:
        raw = get_producao_subitems()
        records = [{
            "item": item,
            "subitem": subitem,
            "quantidade": normalize_quantity(qty_str)
        } for item, subitem, qty_str in raw]

        if records:
            save_producao_records(records)
            logger.info(f"{len(records)} registros de produção salvos.")
            save_execution_status(ExecutionStatusEnum.success, tab)
        else:
            msg = "Nenhum registro válido encontrado para produção."
            logger.warning(msg)
            save_execution_status(ExecutionStatusEnum.error, tab, msg)

    except Exception as e:
        msg = str(e)
        logger.error(f"Erro no ETL de produção: {msg}")
        save_execution_status(ExecutionStatusEnum.error, tab, msg)


def process_and_save_commercializacao():
    tab = ExecutionTabEnum.comercializacao
    try:
        raw = get_commercializacao_subitems()
        records = [{
            "item": item,
            "subitem": subitem,
            "quantidade": normalize_quantity(qty_str)
        } for item, subitem, qty_str in raw]

        if records:
            save_commercializacao_records(records)
            logger.info(f"{len(records)} registros de comercialização salvos.")
            save_execution_status(ExecutionStatusEnum.success, tab)
        else:
            msg = "Nenhum registro válido encontrado para comercialização."
            logger.warning(msg)
            save_execution_status(ExecutionStatusEnum.error, tab, msg)

    except Exception as e:
        msg = str(e)
        logger.error(f"Erro no ETL de comercialização: {msg}")
        save_execution_status(ExecutionStatusEnum.error, tab, msg)


def process_and_save_processamento():
    tab = ExecutionTabEnum.processamento
    try:
        raw = get_all_processamento_data()
        records = []
        for category, variety, qty_str, grape_type_str in raw:
            try:
                grape_type_enum = GrapeTypeEnum(grape_type_str)
            except ValueError:
                logger.warning(f"Grape type inválido ignorado: {grape_type_str}")
                continue

            records.append({
                "category": category,
                "variety": variety,
                "quantidade": normalize_quantity(qty_str),
                "grape_type": grape_type_enum,
            })

        if records:
            save_processamento_records(records)
            logger.info(f"{len(records)} registros de processamento salvos.")
            save_execution_status(ExecutionStatusEnum.success, tab)
        else:
            msg = "Nenhum registro válido encontrado para processamento."
            logger.warning(msg)
            save_execution_status(ExecutionStatusEnum.error, tab, msg)

    except Exception as e:
        msg = str(e)
        logger.error(f"Erro no ETL de processamento: {msg}")
        save_execution_status(ExecutionStatusEnum.error, tab, msg)


def process_and_save_exportacao(section_key, save_func, tab_enum):
    try:
        raw = get_exportacao_data_by_section(section_key)
        records = [{
            "pais": pais,
            "quantidade_kg": normalize_quantity(qtd),
            "valor_usd": normalize_quantity(valor)
        } for pais, qtd, valor, _ in raw]

        if records:
            save_func(records)
            logger.info(f"{len(records)} registros de exportação salvos para {tab_enum}.")
            save_execution_status(ExecutionStatusEnum.success, tab_enum)
        else:
            msg = f"Nenhum registro válido encontrado para {tab_enum.value}."
            logger.warning(msg)
            save_execution_status(ExecutionStatusEnum.error, tab_enum, msg)

    except Exception as e:
        msg = str(e)
        logger.error(f"Erro no ETL de exportação ({tab_enum.value}): {msg}")
        save_execution_status(ExecutionStatusEnum.error, tab_enum, msg)


if __name__ == "__main__":
    logger.info("### Iniciando processamento completo da API FIAP... ###")
    logger.info("#####################################################")

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

    # Exportações (executadas separadamente)
    process_and_save_exportacao("vinhos_de_mesa", save_exportacao_vinhos_de_mesa, ExecutionTabEnum.exportacao_tab_subopt_01)
    process_and_save_exportacao("espumantes", save_exportacao_espumantes, ExecutionTabEnum.exportacao_tab_subopt_02)
    process_and_save_exportacao("uvas_frescas", save_exportacao_uvas_frescas, ExecutionTabEnum.exportacao_tab_subopt_03)
    process_and_save_exportacao("suco_de_uva", save_exportacao_suco_uva, ExecutionTabEnum.exportacao_tab_subopt_04)