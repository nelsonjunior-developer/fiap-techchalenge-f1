from typing import Optional
from pydantic import BaseModel, validator
from captura.exceptions import InvalidDataError
from captura.scrapers.producao_scraper import get_item_subitems


class ProducaoRecord(BaseModel):
    item: str
    subitem: str
    quantidade: Optional[int]

    @validator('item', 'subitem')
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Campo vazio não permitido")
        return v.strip()


def normalize_quantity(qty_str: str) -> Optional[int]:
    """
    Converte uma string de quantidade no formato '27.910.299' para int,
    ou retorna None se for '-' ou string vazia.
    """
    clean = qty_str.strip()
    if clean in ('-', ''):
        return None
    try:
        return int(clean.replace('.', ''))
    except ValueError as e:
        raise InvalidDataError(f"Quantidade inválida: {qty_str}") from e

