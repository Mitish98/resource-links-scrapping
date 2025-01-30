import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import logging

# Configuração do logging
logging.basicConfig(
    filename="scraping_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def log_message(message):
    """Registra a mensagem no console e no arquivo de log."""
    print(message)
    logging.info(message)

def get_all_links(domain):
    visited = set()  # URLs já acessadas
    to_visit = {domain}  # URLs a visitar
    collected_links = []  # Lista de tuplas (origem, link encontrado)

    log_message(f"🔍 Iniciando scraping no domínio: {domain}")

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue  # Evita acessar a mesma URL mais de uma vez
        visited.add(url)

        log_message(f"🌐 Acessando: {url}")

        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                log_message(f"❌ Erro {response.status_code} ao acessar {url}")
                continue
        except requests.RequestException as e:
            log_message(f"⚠️ Falha ao acessar {url}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Captura qualquer link na página
        for tag in soup.find_all(["a", "link", "script", "img"]):
            attr = "href" if tag.name in ["a", "link"] else "src"
            link = tag.get(attr)

            if link:
                full_url = urljoin(url, link)
                if full_url not in [l[1] for l in collected_links]:  # Evita duplicatas
                    collected_links.append((url, full_url))  # Salva (origem, link)
                    log_message(f"✅ Link encontrado: {full_url} (Origem: {url})")

                    # Se for um link interno, adiciona para futuras visitas
                    if urlparse(full_url).netloc == urlparse(domain).netloc:
                        to_visit.add(full_url)

    log_message("✅ Coleta finalizada!")
    return collected_links

def save_to_excel(links, filename="links_site.xlsx"):
    df = pd.DataFrame(links, columns=["Origem", "URL Encontrada"])
    df.to_excel(filename, index=False)
    log_message(f"📂 Lista de URLs salva em {filename}")

# Exemplo de uso
dominio = input("Digite a URL: ")
links = get_all_links(dominio)
save_to_excel(links)
