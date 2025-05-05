# captura/processamento_scraper.py

import requests
from bs4 import BeautifulSoup
import logging
from captura import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_all_processamento_data():
    """
    Coleta dados das 3 páginas do processamento (viníferas, americanas e híbridas, uvas de mesa),
    retornando uma lista de tuplas: (category, variety, quantidade, grape_type).
    """
    urls = {
        "viniferas": config.URL_PROCESSAMENTO_VINIFERAS,
        "americanas_e_hibridas": config.URL_PROCESSAMENTO_AMERICANAS_HIBRIDAS,
        "uvas_de_mesa": config.URL_PROCESSAMENTO_UVAS_MESA,
    }

    all_data = []

    for grape_type, url in urls.items():
        try:
            logging.info(f"Baixando página de Processamento: {url}")
            resp = requests.get(url, timeout=config.HTTP_TIMEOUT)
            resp.raise_for_status()

            if 'text/html' not in resp.headers.get('Content-Type', ''):
                logging.error(f"Conteúdo inválido retornado para {grape_type}")
                raise ValueError("O conteúdo retornado não é HTML.")

            soup = BeautifulSoup(resp.text, 'html.parser')
            table = soup.find('table', class_='tb_base tb_dados')

            current_category = None
            for tr in table.tbody.find_all('tr'):
                tds = tr.find_all('td')
                name = tds[0].get_text(strip=True)
                classes = tds[0].get('class', [])
                quantity = tds[1].get_text(strip=True)

                if 'tb_item' in classes:
                    current_category = name
                elif 'tb_subitem' in classes and current_category:
                    all_data.append((current_category, name, quantity, grape_type))

        except Exception as e:
            logging.error(f"Erro ao processar página {grape_type}: {e}")
            raise

    return all_data