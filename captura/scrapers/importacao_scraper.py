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
from time import sleep

logger = logging.getLogger(__name__)

# Mapping básico de categorias para URLs base sem parâmetro de ano
URLS_IMPORTACAO = {
    "vinhos_de_mesa": URL_IMPORTACAO_VINHOS_MESA,
    "espumantes": URL_IMPORTACAO_ESPUMANTES,
    "uvas_frescas": URL_IMPORTACAO_UVAS_FRESCAS,
    "uvas_passas": URL_IMPORTACAO_UVAS_PASSAS,
    "suco_de_uva": URL_IMPORTACAO_SUCO_UVA,
}


# Ajusta URL para incluir ano explicitamente
def _build_url(base_url: str, year: int) -> str:
    if "ano=" not in base_url:
        if "?" in base_url:
            return f"{base_url}&ano={year}"
        return f"{base_url}?ano={year}"
    return base_url


def get_importacao_data_by_section(section_key: str, ano: int) -> list[tuple[str, str, str]]:
    """
    Raspagem de um ano específico para uma categoria de importação.
    Retorna lista de tuplas (pais, quantidade_kg, valor_usd).
    """
    if section_key not in URLS_IMPORTACAO:
        raise ValueError(f"Categoria inválida de importação: {section_key}")

    base_url = URLS_IMPORTACAO[section_key]
    url = f"{base_url}&ano={ano}"
    logger.info(f"Baixando dados de importação: {section_key} - {ano} - {url}")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            tabela = soup.find("table", class_="tb_dados")

            if not tabela:
                raise ScrapeError(f"Tabela de dados não encontrada para {section_key} ({ano})")

            linhas = tabela.find_all("tr")
            dados = []

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
            if attempt == MAX_RETRIES:
                raise ScrapeError(f"Falha ao obter dados de {section_key} para o ano {ano}") from e

        sleep(1.5)


def get_importacao_data_all_years(section_key: str) -> dict[int, list[tuple[str, str, str]]]:
    """
    Raspagem de todos os anos disponíveis (1970-2024) para a categoria.
    Retorna um dicionário {ano: [(pais, quantidade, valor), ...]}.
    """
    results_by_year = {}
    for year in range(1970, 2025):
        try:
            ano_data = get_importacao_data_by_section(section_key, year)
            logger.info(f"{len(ano_data)} registros coletados para {section_key} - {year}")
            # remove o 4º e 5º campos, pois processor espera 3 valores por tupla
            results_by_year[year] = [(pais, qtd, valor) for pais, qtd, valor, _, _ in ano_data]
        except Exception as e:
            logger.warning(f"Erro ao coletar {section_key} - {year}: {e}")
            results_by_year[year] = []
        sleep(1.5)
    return results_by_year
