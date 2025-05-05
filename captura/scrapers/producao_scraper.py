import requests
from bs4 import BeautifulSoup
import logging
from captura import config

# Configure o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_producao_page():
    """
    Faz o download do HTML da página de Produção usando as configurações do módulo config.
    """
    logging.info("Iniciando o download da página de produção...")
    resp = requests.get(config.URL_PRODUCAO, timeout=config.HTTP_TIMEOUT)
    resp.raise_for_status()
    logging.info("Download concluído com sucesso!")
    # Verifica se o conteúdo da resposta é HTML
    if 'text/html' not in resp.headers.get('Content-Type', ''):
        logging.error("O conteúdo retornado não é HTML.")
        raise ValueError("O conteúdo retornado não é HTML.")
    
    return resp.text

def get_item_subitems():
    html = fetch_producao_page()
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='tb_base tb_dados')

    if not table or not table.tbody:
        raise RuntimeError("Tabela de dados não encontrada na página de produção.")

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
        raise RuntimeError("Nenhum dado encontrado na tabela de produção.")

    return results

if __name__ == "__main__":
    data = get_item_subitems()
    # Loga cada linha de dados no formato desejado
    # for item, subitem, quantidade in data:
    #     logging.info(f"{item}, {subitem}, {quantidade}")