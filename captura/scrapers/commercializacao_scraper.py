import requests
from bs4 import BeautifulSoup
import logging
from captura import config

# Configure o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_commercializacao_page():
    """
    Faz o download do HTML da página de Comercialização usando a URL do config.
    """
    logging.info("Baixando página de Comercialização...")
    resp = requests.get(config.URL_COMERCIALIZACAO, timeout=config.HTTP_TIMEOUT)
    resp.raise_for_status()

    if 'text/html' not in resp.headers.get('Content-Type', ''):
        logging.error("Conteúdo inválido retornado.")
        raise ValueError("O conteúdo retornado não é HTML.")
    
    return resp.text


def get_item_subitems():
    """
    Retorna uma lista de tuplas (item, subitem, quantidade) extraídas da tabela de comercialização.
    Lança exceção se nenhum dado for encontrado.
    """
    html = fetch_commercializacao_page()
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='tb_base tb_dados')

    if not table or not table.tbody:
        raise RuntimeError("Tabela de dados não encontrada na página de comercialização.")

    results = []
    current_item = None
    for tr in table.tbody.find_all('tr'):
        tds = tr.find_all('td')
        name = tds[0].get_text(strip=True)
        classes = tds[0].get('class', [])
        quantity = tds[1].get_text(strip=True)

        if 'tb_item' in classes:
            current_item = name
        elif 'tb_subitem' in classes and current_item:
            results.append((current_item, name, quantity))

    if not results:
        raise RuntimeError("Nenhum dado encontrado na tabela de comercialização.")

    return results