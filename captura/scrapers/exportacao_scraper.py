# captura/scrapers/exportacao_scraper.py

import logging
import requests
from bs4 import BeautifulSoup
from time import sleep

from captura import config
from captura.exceptions import ScrapeError

logger = logging.getLogger(__name__)

EXPORTACAO_URLS = {
    "vinhos_de_mesa": config.URL_EXPORTACAO_VINHOS_MESA,
    "espumantes": config.URL_EXPORTACAO_ESPUMANTES,
    "uvas_frescas": config.URL_EXPORTACAO_UVAS_FRESCAS,
    "suco_de_uva": config.URL_EXPORTACAO_SUCO_UVA,
}


def _build_export_url(base_url: str, year: int) -> str:
    if "ano=" not in base_url:
        if "?" in base_url:
            return f"{base_url}&ano={year}"
        return f"{base_url}?ano={year}"
    return base_url


def get_exportacao_data_by_section(section_key: str, ano: int) -> list[tuple[str, str, str]]:
    """
    Raspagem de um ano específico para uma categoria de exportação.
    Retorna lista de tuplas (pais, quantidade_kg, valor_usd).
    """
    if section_key not in EXPORTACAO_URLS:
        raise ValueError(f"Categoria inválida de exportação: {section_key}")

    base_url = EXPORTACAO_URLS[section_key]
    url = _build_export_url(base_url, ano)
    logger.info(f"Baixando dados de exportação: {section_key} - {ano} - {url}")

    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=config.HTTP_TIMEOUT)
            response.raise_for_status()

            if "text/html" not in response.headers.get("Content-Type", ""):
                raise ScrapeError(f"Conteúdo inválido recebido para {section_key} - {ano}")

            soup = BeautifulSoup(response.text, "html.parser")
            tabela = soup.find("table", class_="tb_dados")

            if not tabela:
                raise ScrapeError(f"Tabela de dados não encontrada para {section_key} ({ano})")

            dados = []
            linhas = tabela.find_all("tr")

            for linha in linhas[1:]:
                colunas = linha.find_all("td")
                if len(colunas) < 3:
                    continue

                pais = colunas[0].get_text(strip=True)
                quantidade = colunas[1].get_text(strip=True)
                valor = colunas[2].get_text(strip=True)

                dados.append((pais, quantidade, valor))

            logger.info(f"{len(dados)} registros coletados para {section_key} - {ano}")
            return dados

        except Exception as e:
            logger.warning(f"[{ano}] Tentativa {attempt} falhou: {e}")
            if attempt == config.MAX_RETRIES:
                raise ScrapeError(f"Falha ao obter dados de {section_key} para o ano {ano}") from e

        sleep(3) # Respeitar o tempo de espera entre as tentativas