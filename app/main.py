# app/main.py

import logging

from fastapi import FastAPI
from app.routes import producao, comercializacao, processamento, importacao, exportacao
from app.routes import auth

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

# Configura o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FIAP Tech Challenge API",
    description="API pública para consulta de dados da vitivinicultura (Embrapa).",
    version="1.0.0",
)

logger.info("### Inciando as rotas ###")
Base.metadata.create_all(bind=engine)

# Registra as rotas de autenticação
app.include_router(auth.router)

# Registra as rotas
app.include_router(producao.router)
app.include_router(comercializacao.router)
app.include_router(processamento.router)
app.include_router(importacao.router)
app.include_router(exportacao.router)

