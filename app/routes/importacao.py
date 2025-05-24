# app/routes/importacao.py

from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from enum import Enum
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database.db import SessionLocal
from database.models.importacao import Importacao
from auth.jwt_handler import verify_token  

router = APIRouter(prefix="/v1/importacao", tags=["Importação"])


class CategoriaEnum(str, Enum):
    espumantes = "espumantes"
    uvas_frescas = "uvas_frescas"
    vinhos_de_mesa = "vinhos_de_mesa"
    suco_de_uva = "suco_de_uva"
    uvas_passas = "uvas_passas"


class ImportacaoOut(BaseModel):
    categoria: str
    pais: str
    ano: int
    quantidade_kg: Optional[float]
    valor_usd: Optional[float]
    created: datetime
    updated: Optional[datetime]

    class Config:
        orm_mode = True


@router.get(
    "/", 
    summary="Listar dados de importação", 
    response_model=List[ImportacaoOut],
    dependencies=[Depends(verify_token)]  # 🔐 Requer autenticação JWT
)
def get_importacao(
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    categoria: Optional[CategoriaEnum] = Query(None, description="Filtrar por categoria"),
):
    session: Session = SessionLocal()
    try:
        query = session.query(Importacao)

        if ano:
            query = query.filter(Importacao.ano == ano)
        if categoria:
            query = query.filter(Importacao.categoria == categoria.value)

        results = query.all()
        return results

    finally:
        session.close()