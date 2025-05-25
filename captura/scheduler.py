import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from captura.processor import (
    run_all_producao_tasks,
    run_all_processamento_tasks,
    run_all_exportacao_tasks,
    run_all_importacao_tasks,
    process_and_save_commercializacao
)
from captura import config

# Configura o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

scheduler = None  # Variável global para controle

def run_all_tasks():
    logger.info("### Execução agendada iniciada ###")
    try:
        process_and_save_commercializacao()
        run_all_producao_tasks()
        run_all_processamento_tasks()
        run_all_exportacao_tasks()
        run_all_importacao_tasks()
        logger.info("### Execução agendada concluída com sucesso ###")
    except Exception as e:
        logger.exception(f"Erro durante execução agendada: {e}")

def start_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        logger.info("Scheduler já está em execução.")
        return

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_all_tasks,
        'interval',
        hours=config.SCHEDULER_INTERVAL_HOURS,
        next_run_time=datetime.now()
    )
    scheduler.start()
    logger.info(f"Scheduler iniciado: rodando a cada {config.SCHEDULER_INTERVAL_HOURS} hora(s).")