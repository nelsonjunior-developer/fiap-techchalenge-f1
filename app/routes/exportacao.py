# app/routes/exportacao.py

from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from database.db import SessionLocal
from database.models.exportacao import Exportacao
from auth.jwt_handler import verify_token  

router = APIRouter(prefix="/v1/exportacao", tags=["Exportação"])


class CategoriaEnum(str, Enum):
    espumantes = "espumantes"
    uvas_frescas = "uvas_frescas"
    vinhos_de_mesa = "vinhos_de_mesa"
    suco_de_uva = "suco_de_uva"


class ExportacaoOut(BaseModel):
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
    summary="Listar dados de exportação", 
    response_model=List[ExportacaoOut],
    dependencies=[Depends(verify_token)]  # 🔐 Requer autenticação JWT
)
def get_exportacao(
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    categoria: Optional[CategoriaEnum] = Query(None, description="Filtrar por categoria"),
):
    session: Session = SessionLocal()
    try:
        query = session.query(Exportacao)

        if ano:
            query = query.filter(Exportacao.ano == ano)
        if categoria:
            query = query.filter(Exportacao.categoria == categoria.value)

        results = query.all()
        return results

    finally:
        session.close()