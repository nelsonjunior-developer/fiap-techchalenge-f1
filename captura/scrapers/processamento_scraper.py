# captura/scrapers/processamento_scraper.py

import requests
from bs4 import BeautifulSoup
import logging
from time import sleep
from captura import config

logger = logging.getLogger(__name__)

URLS_PROCESSAMENTO = {
    "viniferas": config.URL_PROCESSAMENTO_VINIFERAS,
    "americanas_e_hibridas": config.URL_PROCESSAMENTO_AMERICANAS_HIBRIDAS,
    "uvas_de_mesa": config.URL_PROCESSAMENTO_UVAS_MESA,
}

def _build_url(base_url: str, ano: int) -> str:
    if "ano=" not in base_url:
        return f"{base_url}&ano={ano}" if "?" in base_url else f"{base_url}?ano={ano}"
    return base_url

def get_all_processamento_data(ano: int) -> list[tuple[str, str, str, str]]:
    """
    Coleta dados de processamento para um ano específico das três seções:
    viníferas, americanas e híbridas, uvas de mesa.
    Retorna lista de tuplas: (categoria, variedade, quantidade, tipo_uva)
    """
    all_data = []

    for grape_type, base_url in URLS_PROCESSAMENTO.items():
        url = _build_url(base_url, ano)
        logger.info(f"Baixando dados de Processamento: {grape_type} - {ano} - {url}")

        try:
            resp = requests.get(url, timeout=config.HTTP_TIMEOUT)
            resp.raise_for_status()

            if 'text/html' not in resp.headers.get('Content-Type', ''):
                logger.error(f"[{ano}] Conteúdo inválido retornado para {grape_type}")
                raise ValueError("Conteúdo não é HTML.")

            soup = BeautifulSoup(resp.text, 'html.parser')
            table = soup.find('table', class_='tb_base tb_dados')

            if not table:
                raise ValueError(f"[{ano}] Tabela de dados não encontrada para {grape_type}")

            current_category = None
            for tr in table.tbody.find_all('tr'):
                tds = tr.find_all('td')
                if not tds:
                    continue

                name = tds[0].get_text(strip=True)
                quantity = tds[1].get_text(strip=True)
                classes = tds[0].get('class', [])

                if 'tb_item' in classes:
                    current_category = name
                elif 'tb_subitem' in classes and current_category:
                    all_data.append((current_category, name, quantity, grape_type))

        except Exception as e:
            logger.warning(f"[{ano}] Erro ao processar {grape_type}: {e}")
            continue

        sleep(1.5)

    logger.info(f"{len(all_data)} registros coletados no processamento para o ano {ano}")
    return all_data