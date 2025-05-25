# create_tables.py
from database.db import Base, engine
import database.models.producao
import database.models.processamento
import database.models.comercializacao
import database.models.importacao
import database.models.exportacao
import database.models.execution_status
import database.models.error_log

import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("### Iniciando criação de tabelas... ###")

try:
    Base.metadata.create_all(bind=engine)
    logger.info("### Tabelas criadas com sucesso. ###")
except Exception as e:
    logger.error(f"Erro ao criar tabelas: {e}")
    sys.exit(1)