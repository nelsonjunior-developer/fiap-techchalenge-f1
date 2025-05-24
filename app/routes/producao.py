from fastapi import APIRouter, Query, Depends, HTTPException, status
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from database.db import SessionLocal
from database.models.producao import Producao
from auth.jwt_handler import verify_token  

router = APIRouter(prefix="/v1/producao", tags=["Produção"])


# Enum com os possíveis valores para filtro por item
class ItemEnum(str, Enum):
    SUCO = "SUCO"
    VINHO_FINO = "VINHO FINO DE MESA (VINIFERA)"
    DERIVADOS = "DERIVADOS"
    VINHO_MESA = "VINHO DE MESA"


# Modelo de resposta com Pydantic
class ProducaoResponse(BaseModel):
    item: str
    subitem: str
    quantidade: Optional[int]
    ano: int
    created: datetime
    updated: Optional[datetime]

    class Config:
        orm_mode = True


@router.get(
    "/",
    summary="Listar dados de produção",
    response_model=List[ProducaoResponse],
)
def get_producao(
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    item: Optional[ItemEnum] = Query(None, description="Filtrar por item"),
    user: dict = Depends(verify_token),  # 🔐 Requer token JWT válido
):
    session: Session = SessionLocal()
    try:
        query = session.query(Producao)

        if ano:
            query = query.filter(Producao.ano == ano)
        if item:
            query = query.filter(Producao.item == item.value)

        return query.all()
    finally:
        session.close()