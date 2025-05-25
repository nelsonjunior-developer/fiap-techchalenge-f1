# app/main.py

import logging

from fastapi import FastAPI
from app.routes import producao, comercializacao, processamento, importacao, exportacao
from app.routes import auth

# IMPORTANTE: importa e inicia o scheduler
from captura.scheduler import start_scheduler

# Configura o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FIAP Tech Challenge API",
    description="API pública para consulta de dados da vitivinicultura (Embrapa).",
    version="1.0.0",
)

logger.info("### Iniciando as rotas ###")

# Registra as rotas de autenticação
app.include_router(auth.router)

# Registra as demais rotas
app.include_router(producao.router)
app.include_router(comercializacao.router)
app.include_router(processamento.router)
app.include_router(importacao.router)
app.include_router(exportacao.router)

# Inicia o agendador
start_scheduler()