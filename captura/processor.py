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

## Função para produção
def process_and_save_producao():
    """
    Processa e salva os dados da aba Produção ano a ano (1970–2024),
    com status individual por ano e tratamento de falhas isoladas.
    """
    tab = ExecutionTabEnum.producao
    total_registros = 0

    for ano in range(1970, 2025):
        try:
            raw = get_producao_subitems(ano)
            registros_ano = [{
                "item": item,
                "subitem": subitem,
                "quantidade": normalize_quantity(qtd),
                "ano": ano
            } for item, subitem, qtd in raw if item and subitem and qtd]

            if registros_ano:
                save_producao_records(registros_ano)
                logger.info(f"{len(registros_ano)} registros salvos para produção em {ano}")
                save_execution_status(ExecutionStatusEnum.success, tab, ano=ano)
                total_registros += len(registros_ano)
            else:
                msg = f"Nenhum dado válido encontrado para produção em {ano}"
                logger.warning(msg)
                save_execution_status(ExecutionStatusEnum.error, tab, error_message=msg, ano=ano)

        except Exception as e:
            msg = f"Erro ao processar ano {ano} (produção): {e}"
            logger.error(msg)
            save_execution_status(ExecutionStatusEnum.error, tab, error_message=msg, ano=ano)

    logger.info(f"Total acumulado de registros salvos para produção: {total_registros}")

## Função para processamento de dados de comercialização
def process_and_save_commercializacao():
    """
    Processa e salva os dados da aba de Comercialização, ano a ano (1970–2024),
    com status individual por ano e tratamento de falhas isoladas.
    """
    tab = ExecutionTabEnum.comercializacao
    total_registros = 0

    for ano in range(1970, 2025):
        try:
            raw = get_commercializacao_subitems(ano)
            registros_ano = [{
                "item": item,
                "subitem": subitem,
                "quantidade": normalize_quantity(qty_str),
                "ano": ano
            } for item, subitem, qty_str in raw if item and subitem and qty_str]

            if registros_ano:
                save_commercializacao_records(registros_ano)
                logger.info(f"{len(registros_ano)} registros salvos para comercialização em {ano}")
                save_execution_status(ExecutionStatusEnum.success, tab, ano=ano)
                total_registros += len(registros_ano)
            else:
                msg = f"Nenhum dado válido encontrado para comercialização em {ano}"
                logger.warning(msg)
                save_execution_status(ExecutionStatusEnum.error, tab, error_message=msg, ano=ano)

        except Exception as e:
            msg = f"Erro ao processar ano {ano} (comercialização): {e}"
            logger.error(msg)
            save_execution_status(ExecutionStatusEnum.error, tab, error_message=msg, ano=ano)

    logger.info(f"Total acumulado de registros salvos para comercialização: {total_registros}")


## Função para processamento de dados de processamento
def process_and_save_processamento():
    """
    Processa e salva os dados da aba de Processamento, ano a ano (1970–2024),
    com status individual por ano e tratamento de falhas isoladas.
    """
    tab = ExecutionTabEnum.processamento
    total_registros = 0

    for ano in range(1970, 2025):
        try:
            raw = get_all_processamento_data(ano)
            registros_ano = []

            for category, variety, qty_str, grape_type_str in raw:
                try:
                    grape_type_enum = GrapeTypeEnum(grape_type_str)
                except ValueError:
                    logger.warning(f"Ano {ano} — Grape type inválido ignorado: {grape_type_str}")
                    continue

                registros_ano.append({
                    "category": category,
                    "variety": variety,
                    "quantidade": normalize_quantity(qty_str),
                    "grape_type": grape_type_enum,
                    "ano": ano
                })

            if registros_ano:
                save_processamento_records(registros_ano)
                logger.info(f"{len(registros_ano)} registros salvos para processamento em {ano}")
                save_execution_status(ExecutionStatusEnum.success, tab, ano=ano)
                total_registros += len(registros_ano)
            else:
                msg = f"Nenhum dado válido encontrado para processamento em {ano}"
                logger.warning(msg)
                save_execution_status(ExecutionStatusEnum.error, tab, error_message=msg, ano=ano)

        except Exception as e:
            msg = f"Erro ao processar ano {ano} (processamento): {e}"
            logger.error(msg)
            save_execution_status(ExecutionStatusEnum.error, tab, error_message=msg, ano=ano)

    logger.info(f"Total acumulado de registros salvos para processamento: {total_registros}")

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

def run_all_commercializacao_tasks():
    try:
        process_and_save_commercializacao()
    except Exception:
        logger.exception("Falha crítica em comercialização.")

def run_all_producao_tasks():
    try:
        process_and_save_producao()
    except Exception:
        logger.exception("Falha crítica em produção.")

def run_all_importacao_tasks():
    tasks = [
        ("vinhos_de_mesa", save_importacao_vinhos_de_mesa, ExecutionTabEnum.importacao_tab_subopt_01),
        ("espumantes", save_importacao_espumantes, ExecutionTabEnum.importacao_tab_subopt_02),
        ("uvas_frescas", save_importacao_uvas_frescas, ExecutionTabEnum.importacao_tab_subopt_03),
        ("uvas_passas", save_importacao_uvas_passas, ExecutionTabEnum.importacao_tab_subopt_04),
        ("suco_de_uva", save_importacao_suco_uva, ExecutionTabEnum.importacao_tab_subopt_05),
    ]
    for section, save_func, tab_enum in tasks:
        try:
            process_and_save_importacao(section, save_func, tab_enum)
        except Exception:
            logger.exception(f"Falha crítica em {tab_enum.value}")

def run_all_exportacao_tasks():
    tasks = [
        ("vinhos_de_mesa", save_exportacao_vinhos_de_mesa, ExecutionTabEnum.exportacao_tab_subopt_01),
        ("espumantes", save_exportacao_espumantes, ExecutionTabEnum.exportacao_tab_subopt_02),
        ("uvas_frescas", save_exportacao_uvas_frescas, ExecutionTabEnum.exportacao_tab_subopt_03),
        ("suco_de_uva", save_exportacao_suco_uva, ExecutionTabEnum.exportacao_tab_subopt_04),
    ]
    for section, save_func, tab_enum in tasks:
        try:
            process_and_save_exportacao(section, save_func, tab_enum)
        except Exception:
            logger.exception(f"Falha crítica em {tab_enum.value}")

def run_all_processamento_tasks():
    try:
        process_and_save_processamento()
    except Exception:
        logger.exception("Falha crítica em processamento.")

#############################################
## Main function to run all scraping tasks ##
#############################################
if __name__ == "__main__":
    
    logger.info("### Iniciando processamento completo da API FIAP... ###")

    # Run commercialização tasks
    run_all_commercializacao_tasks()
    
    # Run production tasks
    run_all_producao_tasks()
    
    # Run all processamento tasks
    run_all_processamento_tasks()

    # Run all exportacao tasks
    run_all_exportacao_tasks()
    
    # Run all importacao tasks
    run_all_importacao_tasks()