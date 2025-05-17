# captura/scrapers/importacao_scraper.py

import logging
import requests
from bs4 import BeautifulSoup
from captura.config import (
    URL_IMPORTACAO_VINHOS_MESA,
    URL_IMPORTACAO_ESPUMANTES,
    URL_IMPORTACAO_UVAS_FRESCAS,
    URL_IMPORTACAO_UVAS_PASSAS,
    URL_IMPORTACAO_SUCO_UVA,
    HTTP_TIMEOUT,
    MAX_RETRIES,
)
from captura.exceptions import ScrapeError

logger = logging.getLogger(__name__)

URLS_IMPORTACAO = {
    "vinhos_de_mesa": URL_IMPORTACAO_VINHOS_MESA,
    "espumantes": URL_IMPORTACAO_ESPUMANTES,
    "uvas_frescas": URL_IMPORTACAO_UVAS_FRESCAS,
    "uvas_passas": URL_IMPORTACAO_UVAS_PASSAS,
    "suco_de_uva": URL_IMPORTACAO_SUCO_UVA,
}


def get_importacao_data_by_section(section_key: str) -> list[tuple[str, str, str, str]]:
    """
    Retorna lista de tuplas (pais, quantidade_kg, valor_usd, categoria)
    para a categoria de importação fornecida.
    """
    if section_key not in URLS_IMPORTACAO:
        raise ValueError(f"Categoria inválida de importação: {section_key}")
    
    url = URLS_IMPORTACAO[section_key]
    logger.info(f"Solicitando dados de importação: {section_key} - {url}")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            tabela = soup.find("table", class_="tb_dados")

            if not tabela:
                raise ScrapeError(f"Tabela de dados não encontrada para {section_key}")

            linhas = tabela.find_all("tr")
            dados = []

            for linha in linhas[1:]:
                colunas = linha.find_all("td")
                if len(colunas) < 3:
                    continue

                pais = colunas[0].get_text(strip=True)
                quantidade = colunas[1].get_text(strip=True)
                valor = colunas[2].get_text(strip=True)

                # Mantém "-" se estiver vazio para tratamento posterior
                dados.append((pais, quantidade, valor, section_key))

            logger.info(f"{len(dados)} registros extraídos de {section_key}")
            return dados

        except Exception as e:
            logger.warning(f"Tentativa {attempt} falhou: {e}")
            if attempt == MAX_RETRIES:
                raise ScrapeError(f"Falha ao obter dados de importação: {section_key}") from e