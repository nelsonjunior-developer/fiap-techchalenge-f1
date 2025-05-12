# captura/scrapers/exportacao_scraper.py

import logging
import requests
from bs4 import BeautifulSoup
from captura import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EXPORTACAO_URLS = {
    "vinhos_de_mesa": (config.URL_EXPORTACAO_VINHOS_MESA, "exportacao_tab_subopt_01"),
    "espumantes":     (config.URL_EXPORTACAO_ESPUMANTES,   "exportacao_tab_subopt_02"),
    "uvas_frescas":   (config.URL_EXPORTACAO_UVAS_FRESCAS, "exportacao_tab_subopt_03"),
    "suco_de_uva":    (config.URL_EXPORTACAO_SUCO_UVA,     "exportacao_tab_subopt_04"),
}

def fetch_exportacao_page(url: str) -> str:
    logger.info(f"Baixando página de Exportação: {url}")
    resp = requests.get(url, timeout=config.HTTP_TIMEOUT)
    resp.raise_for_status()

    if 'text/html' not in resp.headers.get('Content-Type', ''):
        logger.error("Conteúdo inválido retornado.")
        raise ValueError("O conteúdo retornado não é HTML.")

    return resp.text

def parse_exportacao_table(html: str) -> list[tuple[str, str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='tb_base tb_dados')
    if not table:
        logger.warning("Tabela de dados não encontrada na página exportação.")
        return []

    results = []
    for tr in table.tbody.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) < 3:
            continue

        pais   = tds[0].get_text(strip=True)
        qtde   = tds[1].get_text(strip=True)
        valor  = tds[2].get_text(strip=True)

        results.append((pais, qtde, valor))
    return results

def get_exportacao_data_by_section(section_key: str) -> list[tuple[str, str, str, str]]:
    if section_key not in EXPORTACAO_URLS:
        raise ValueError(f"Chave de seção inválida: {section_key}")

    url, tab_enum_str = EXPORTACAO_URLS[section_key]
    try:
        html = fetch_exportacao_page(url)
        rows = parse_exportacao_table(html)
        return [(pais, qtde, valor, tab_enum_str) for pais, qtde, valor in rows]
    except Exception as e:
        logger.error(f"Erro ao processar página {section_key}: {e}")
        raise
