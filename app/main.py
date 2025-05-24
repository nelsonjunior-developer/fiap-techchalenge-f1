# app/main.py

from fastapi import FastAPI
from app.routes import producao, comercializacao, processamento, importacao, exportacao
from app.routes import auth

app = FastAPI(
    title="FIAP Tech Challenge API",
    description="API pública para consulta de dados da vitivinicultura (Embrapa).",
    version="1.0.0",
)

# Registra as rotas de autenticação
app.include_router(auth.router)

# Registra as rotas
app.include_router(producao.router)
app.include_router(comercializacao.router)
app.include_router(processamento.router)
app.include_router(importacao.router)
app.include_router(exportacao.router)

