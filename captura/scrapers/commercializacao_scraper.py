import requests
from bs4 import BeautifulSoup
import logging
from time import sleep
from captura import config

logger = logging.getLogger(__name__)

MAX_RETRIES = config.MAX_RETRIES
TIMEOUT = config.HTTP_TIMEOUT

def _build_url(base_url: str, year: int) -> str:
    if "ano=" not in base_url:
        if "?" in base_url:
            return f"{base_url}&ano={year}"
        return f"{base_url}?ano={year}"
    return base_url

def fetch_commercializacao_page(year: int) -> str:
    url = _build_url(config.URL_COMERCIALIZACAO, year)
    logger.info(f"Baixando dados da Comercialização - Ano {year} - {url}")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            if 'text/html' not in resp.headers.get('Content-Type', ''):
                raise ValueError(f"Ano {year}: Conteúdo inválido retornado (não é HTML)")
            return resp.text
        except Exception as e:
            logger.warning(f"[{year}] Tentativa {attempt} falhou: {e}")
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"Falha ao obter dados de comercialização para o ano {year}") from e
        sleep(1.5)

def get_item_subitems(year: int) -> list[tuple[str, str, str]]:
    """
    Retorna uma lista de tuplas (item, subitem, quantidade) extraídas da tabela de comercialização
    para um determinado ano.
    """
    html = fetch_commercializacao_page(year)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='tb_base tb_dados')

    if not table or not table.tbody:
        raise RuntimeError(f"Tabela de dados não encontrada para o ano {year} na aba de comercialização.")

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

    logger.info(f"{len(results)} registros extraídos da aba comercialização - {year}")
    return results