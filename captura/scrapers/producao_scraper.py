import requests
from bs4 import BeautifulSoup
import logging
from captura import config
from time import sleep

# Configura o logger
logger = logging.getLogger(__name__)

def _build_url(base_url: str, year: int) -> str:
    if "ano=" not in base_url:
        if "?" in base_url:
            return f"{base_url}&ano={year}"
        return f"{base_url}?ano={year}"
    return base_url

def fetch_producao_page(year: int) -> str:
    """
    Faz o download do HTML da página de Produção para um ano específico.
    """
    url = _build_url(config.URL_PRODUCAO, year)
    logger.info(f"Baixando dados da Produção - Ano {year} - {url}")

    try:
        resp = requests.get(url, timeout=config.HTTP_TIMEOUT)
        resp.raise_for_status()

        if 'text/html' not in resp.headers.get('Content-Type', ''):
            logger.error(f"Ano {year}: Conteúdo inválido retornado (não é HTML)")
            raise ValueError("O conteúdo retornado não é HTML.")
        return resp.text

    except Exception as e:
        logger.warning(f"[{year}] Erro ao baixar a página de produção: {e}")
        raise

def get_item_subitems(year: int) -> list[tuple[str, str, str]]:
    """
    Faz o parsing da tabela de produção para um determinado ano.
    Retorna uma lista de tuplas: (item, subitem, quantidade).
    """
    html = fetch_producao_page(year)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='tb_base tb_dados')

    if not table or not table.tbody:
        raise RuntimeError(f"Tabela de dados não encontrada para o ano {year}.")

    results = []
    current_item = None
    for tr in table.tbody.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) < 2:
            continue

        name = tds[0].get_text(strip=True)
        quantity = tds[1].get_text(strip=True)
        classes = tds[0].get('class', [])

        if 'tb_item' in classes:
            current_item = name
        elif 'tb_subitem' in classes and current_item:
            results.append((current_item, name, quantity))

    logger.info(f"{len(results)} registros extraídos para Produção - {year}")
    return results