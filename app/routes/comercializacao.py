from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from enum import Enum
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database.db import SessionLocal
from database.models.comercializacao import Comercializacao
from auth.jwt_handler import verify_token  

router = APIRouter(prefix="/v1/comercializacao", tags=["Comercialização"])

# Enum com os possíveis valores de item
class ItemEnum(str, Enum):
    VINHO_MESA = "VINHO DE MESA"
    OUTROS = "OUTROS PRODUTOS COMERCIALIZADOS"
    SUCO = "SUCO DE UVAS"
    ESPUMANTES = "ESPUMANTES"
    VINHO_ESPECIAL = "VINHO ESPECIAL"
    VINHO_FINO = "VINHO FINO DE MESA"

# Response model com Pydantic
class ComercializacaoResponse(BaseModel):
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
    summary="Listar dados de comercialização", 
    response_model=List[ComercializacaoResponse],
    dependencies=[Depends(verify_token)]  # 🔐 Protege a rota
)
def get_comercializacao(
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    item: Optional[ItemEnum] = Query(None, description="Filtrar por item"),
):
    session: Session = SessionLocal()
    try:
        query = session.query(Comercializacao)

        if ano:
            query = query.filter(Comercializacao.ano == ano)
        if item:
            query = query.filter(Comercializacao.item == item.value)

        return query.all()
    finally:
        session.close()