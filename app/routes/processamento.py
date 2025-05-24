from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from enum import Enum
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models.processamento import Processamento, GrapeTypeEnum
from pydantic import BaseModel
from datetime import datetime

from auth.jwt_handler import verify_token  

router = APIRouter(prefix="/v1/processamento", tags=["Processamento"])


class CategoryEnum(str, Enum):
    BRANCAS = "BRANCAS"
    TINTAS = "TINTAS"
    BRANCAS_E_ROSADAS = "BRANCAS E ROSADAS"


class ProcessamentoResponse(BaseModel):
    category: str
    variety: str
    quantidade: Optional[int]
    grape_type: GrapeTypeEnum
    ano: int
    created: datetime
    updated: Optional[datetime]

    class Config:
        orm_mode = True


@router.get(
    "/", 
    summary="Listar dados de processamento", 
    response_model=List[ProcessamentoResponse],
    dependencies=[Depends(verify_token)]  # 🔐 Rota protegida
)
def get_processamento(
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    category: Optional[CategoryEnum] = Query(None, description="Filtrar por categoria"),
    grape_type: Optional[GrapeTypeEnum] = Query(None, description="Filtrar por tipo de uva"),
):
    session: Session = SessionLocal()
    try:
        query = session.query(Processamento)

        if ano:
            query = query.filter(Processamento.ano == ano)
        if category:
            query = query.filter(Processamento.category == category.value)
        if grape_type:
            query = query.filter(Processamento.grape_type == grape_type.value)

        return query.all()
    finally:
        session.close()