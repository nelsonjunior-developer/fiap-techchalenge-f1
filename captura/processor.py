# captura/processor.py

import logging
from captura.scrapers.importacao_scraper import get_importacao_data_by_section
from captura.scrapers.producao_scraper import get_item_subitems as get_producao_subitems
from captura.scrapers.commercializacao_scraper import get_item_subitems as get_commercializacao_subitems
from captura.scrapers.processamento_scraper import get_all_processamento_data
from captura.scrapers.exportacao_scraper import get_exportacao_data_by_section
from captura.scrapers.importacao_scraper import get_importacao_data_all_years
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
from database.repos.importacao_repo import (
    save_importacao_vinhos_de_mesa,
    save_importacao_espumantes,
    save_importacao_uvas_frescas,
    save_importacao_uvas_passas,
    save_importacao_suco_uva
)
from database.repos.execution_repo import save_execution_status
from database.models.execution_status import ExecutionStatusEnum, ExecutionTabEnum
from database.models.processamento import GrapeTypeEnum

# Configura o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Garante que as tabelas existam
Base.metadata.create_all(bind=engine)

## Função para normalizar a quantidade
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

## Função para processamento de dados de comercialização
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

## Função para processamento de dados de processamento
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

### Funções para importação
def process_and_save_importacao(section_key, save_func, tab_enum):
    """
    Processa e salva os dados de importação de uma seção específica ano a ano,
    garantindo que cada ano seja tratado de forma isolada (raspagem, persistência e status).
    """
    total_registros = 0

    for ano in range(1970, 2025):
        try:
            rows = get_importacao_data_by_section(section_key, ano)
            registros_ano = []
            for row in rows:
                if len(row) == 3:
                    pais, qtd, valor = row
                    registros_ano.append({
                        "pais": pais,
                        "quantidade_kg": normalize_quantity(qtd),
                        "valor_usd": normalize_quantity(valor),
                        "ano": ano
                    })
                else:
                    logger.warning(f"Formato inválido detectado no ano {ano}: {row}")

            if registros_ano:
                save_func(registros_ano)
                logger.info(f"{len(registros_ano)} registros salvos para {tab_enum.value} em {ano}")
                save_execution_status(ExecutionStatusEnum.success, tab_enum, ano=ano)
                total_registros += len(registros_ano)
            else:
                msg = f"Nenhum dado válido para {tab_enum.value} em {ano}"
                logger.warning(msg)
                save_execution_status(ExecutionStatusEnum.error, tab_enum, error_message=msg, ano=ano)

        except Exception as e:
            msg = f"Erro ao processar ano {ano} ({tab_enum.value}): {e}"
            logger.error(msg)
            save_execution_status(ExecutionStatusEnum.error, tab_enum, error_message=msg, ano=ano)

    logger.info(f"Total acumulado de registros salvos para {tab_enum.value}: {total_registros}")


## Funções para exportação
def process_and_save_exportacao(section_key, save_func, tab_enum):
    """
    Processa e salva os dados de exportação de uma seção específica ano a ano,
    com status individual por ano e tratamento de falhas isoladas.
    """
    total_registros = 0

    for ano in range(1970, 2025):
        try:
            rows = get_exportacao_data_by_section(section_key, ano)
            registros_ano = []

            for pais, qtd, valor in rows:
                registros_ano.append({
                    "pais": pais,
                    "quantidade_kg": normalize_quantity(qtd),
                    "valor_usd": normalize_quantity(valor),
                    "ano": ano
                })

            if registros_ano:
                save_func(registros_ano)
                logger.info(f"{len(registros_ano)} registros salvos para {tab_enum.value} em {ano}")
                save_execution_status(ExecutionStatusEnum.success, tab_enum, ano=ano)
                total_registros += len(registros_ano)
            else:
                msg = f"Nenhum dado válido para {tab_enum.value} em {ano}"
                logger.warning(msg)
                save_execution_status(ExecutionStatusEnum.error, tab_enum, error_message=msg, ano=ano)

        except Exception as e:
            msg = f"Erro ao processar ano {ano} ({tab_enum.value}): {e}"
            logger.error(msg)
            save_execution_status(ExecutionStatusEnum.error, tab_enum, error_message=msg, ano=ano)

    logger.info(f"Total acumulado de registros salvos para {tab_enum.value}: {total_registros}")


#############################################
## Main function to run all scraping tasks ##
#############################################
if __name__ == "__main__":
    
    logger.info("### Iniciando processamento completo da API FIAP... ###")
    
    

    # try:
    #     process_and_save_commercializacao()
    # except Exception:
    #     logger.exception("Falha crítica em comercialização.")

    # try:
    #     process_and_save_producao()
    # except Exception:
    #     logger.exception("Falha crítica em produção.")

    # try:
    #     process_and_save_processamento()
    # except Exception:
    #     logger.exception("Falha crítica em processamento.")







    # Run all exportacao tasks
    try:
        process_and_save_exportacao("vinhos_de_mesa", save_exportacao_vinhos_de_mesa, ExecutionTabEnum.exportacao_tab_subopt_01)
    except Exception:
        logger.exception("Falha crítica em exportacao_tab_subopt_01")

    try:
        process_and_save_exportacao("espumantes", save_exportacao_espumantes, ExecutionTabEnum.exportacao_tab_subopt_02)
    except Exception:
        logger.exception("Falha crítica em exportacao_tab_subopt_02")

    try:
        process_and_save_exportacao("uvas_frescas", save_exportacao_uvas_frescas, ExecutionTabEnum.exportacao_tab_subopt_03)
    except Exception:
        logger.exception("Falha crítica em exportacao_tab_subopt_03")

    try:
        process_and_save_exportacao("suco_de_uva", save_exportacao_suco_uva, ExecutionTabEnum.exportacao_tab_subopt_04)
    except Exception:
        logger.exception("Falha crítica em exportacao_tab_subopt_04")

    



    # Run all importacao tasks
   # run_all_importacao_tasks()