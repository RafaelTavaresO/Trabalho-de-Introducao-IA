import yfinance as finance
import requests
from bs4 import BeautifulSoup
import re

def scrape_infomoney(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, "html.parser")

    # ------------------------
    # 1. Título
    # ------------------------
    titulo_tag = soup.find("h1")
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else None

    # ------------------------
    # 2. Data (se existir)
    # ------------------------
    data_tag = soup.find("time")
    data = data_tag.get_text(strip=True) if data_tag else None

    # ------------------------
    # 3. Conteúdo principal
    # ------------------------
    article = soup.find("article", class_="im-article")
    conteudo_lista = []

    if article:
        for tag in article.descendants:

            # Ignorar anúncios e CTAs
            if tag.name == "div":
                if tag.get("data-ad-type"):
                    continue
                if tag.get("data-ds-component") == "ad":
                    continue
                if "cta-middle" in tag.get("class", []):
                    continue

            # Parágrafos puros
            if tag.name == "p":
                texto = tag.get_text(strip=True)
                if texto and texto.lower() not in [
                    "publicidade",
                    "continua depois da publicidade",
                ]:
                    conteudo_lista.append(texto)

            # Subtítulos
            if tag.name in ["h2", "h3"]:
                texto = tag.get_text(strip=True)
                if texto:
                    conteudo_lista.append("\n" + texto + "\n")

    conteudo = "\n".join(conteudo_lista)

    # ------------------------
    # 4. Retorno estruturado
    # ------------------------
    return {
        "url": url,
        "titulo": titulo,
        "data": data,
        "conteudo": conteudo,
        "fonte": "InfoMoney"
    }


def carregar_links(path="noticias-CPLE6.txt"):
    links = []
    with open(path, "r", encoding="utf-8") as f:
        for linha in f:
            link = re.search(r'https?://\S+', linha)
            if link:
                links.append(link.group())
    return links


def filtrar_noticias_brasileira(noticias):
    retorno = []
    for n in noticias:
        if n.get("lang", "").startswith("pt") or n.get("region", "").lower() == "br":
            retorno.append(n)
    
    return retorno


def processar_empresa(ticker_str):
    ticker = finance.Ticker(ticker_str)

    print("\n=== DADOS HISTÓRICOS ===")
    dados = ticker.history(period="1y")
    print(dados.tail())
    dados.to_csv(f"{ticker_str}_historico.csv")

    print("\n=== NOTÍCIAS ===")
    noticias = ticker.news[:10] 

    #noticias = filtrar_noticias_brasileira(noticias)  # buscar 15 notícias
    for i, n in enumerate(noticias, start=1):
        print(f"{i}. {n}")
        #print(f"{i}. {n['content']['title']}")
        #print(n['content'])
        #print(n)


    return dados, noticias


# Executar para COPEL
#processar_empresa("CPLE6.SA")
# Exemplo de uso
links = carregar_links()
print(links)

noticias = []

i = 0
for link in links:
    try:
        dados = scrape_infomoney(link)
        noticias.append(dados)
        print("Coletado:", dados["titulo"])
    except Exception as e:
        print("Erro ao coletar", link, e)