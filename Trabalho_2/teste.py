import yfinance as finance
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

class Noticia():
    def __init__(self):
        self.titulo = ""
        self.data = ""
        self.conteudo = ""
        self.url = ""
        self.fonte = ""

    def carrega_noticia(self, titulo, data, conteudo, url):
        self.titulo = titulo
        self.data = data
        self.conteudo = conteudo
        self.url = url

def converte_data_infomoney(data):
    data_str = data
    dt = datetime.strptime(data_str, "%d/%m/%Y %Hh%M")
    data_formatada = dt.strftime("%Y-%m-%d")

    return data_formatada

def converte_data_yahoo(data):
    data_str = data
    dt = datetime.strptime(data_str, "%B %d, %Y")
    data_formatada = dt.strftime("%Y-%m-%d")

    return data_formatada


def limpar_texto(texto):
    # transforma em minúsculas
    texto = texto.lower()

    # remove caracteres não alfabéticos (mantém acentos)
    texto = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", " ", texto)

    # troca múltiplos espaços por 1 espaço
    texto = re.sub(r"\s+", " ", texto).strip()

    # divide em lista de palavras
    palavras = texto.split(" ")

    return palavras

def limpar_lista_textos(lista_textos):
    palavras = []
    for trecho in lista_textos:
        palavras.extend(limpar_texto(trecho))
    return palavras

def scrape_yahoofinance(noticia):
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(noticia.url, headers=headers).text
    soup = BeautifulSoup(html, "html.parser")

    # ------------------------
    # 2. Data (se existir)
    # ------------------------
    data_tag = soup.find("time")
    data = data_tag.get_text(strip=True) if data_tag else None
    data = converte_data_yahoo(data)

    # ------------------------
    # 3. Conteúdo principal
    # ------------------------
    #article = soup.find("div.bodyItems-wrapper")
    #conteudo_lista = []

    textos = []
    conteudo = soup.find("div", class_="bodyItems-wrapper")

    for p in conteudo.find_all("p"):
        txt = p.get_text(strip=True)
        if txt:
            textos.append(txt)

    textos = limpar_lista_textos(textos)

    a = Noticia()
    a.carrega_noticia(noticia.titulo, data, textos, noticia.url)
    a.fonte = noticia.fonte


    return a
    
def scrape_infomoney(noticia):
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(noticia.url, headers=headers).text
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
    data = converte_data_infomoney(data)

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

    texto = limpar_texto(conteudo)

    # ------------------------
    # 4. Retorno estruturado
    # ------------------------
    a = Noticia()
    a.carrega_noticia(titulo, data, texto, noticia.url)
    a.fonte = noticia.fonte

    return a

def carregar_links(path="noticias-CPLE6.txt"):
    links = []
    with open(path, "r", encoding="utf-8") as f:
        for linha in f:
            link = re.search(r'https?://\S+', linha)
            if link:
                a = Noticia()
                a.url = link.group()
                a.fonte = "InfoMoney"
                links.append(a)
    return links

def processar_empresa(ticker_str):
    noticias = []
    ticker = finance.Ticker(ticker_str)

    dados = ticker.history(period="1y")
    dados.to_csv(f"{ticker_str}_historico.csv")

    ntcia = ticker.news[:10] 

    for n in ntcia:
        a = Noticia()
        a.titulo = n['content']['title']
        a.url = n['content']['canonicalUrl']['url']
        a.fonte = "YahooFinance"

        if "finance.yahoo.com"  in a.url:
            noticias.append(a)
    #noticias = filtrar_noticias_brasileira(noticias)  # buscar 15 notícias
    # for i, n in enumerate(noticias, start=1):
    #     print(f"{i}. {n}")
    #     #print(f"{i}. {n['content']['title']}")
    #     #print(n['content'])
    #     #print(n)

    return dados, noticias


# Exemplo de uso
noticias = carregar_links()

dados, noticia_1 = processar_empresa("CPLE6.SA")

for n in noticia_1:
    noticias.append(n)

noticias_dados = []

i = 1
for noticia in noticias:
    print(f"\nNº{i} - Notícia: {noticia.url}")
    try:
        with open(f"Noticia_{i}.txt", "w") as arq:
            if noticia.fonte == "InfoMoney":
                noticia = scrape_infomoney(noticia)
                noticias_dados.append(noticia)
            else:              
                noticia = scrape_yahoofinance(noticia)
                noticias_dados.append(noticia)

            print(f"Coletado: {noticia.titulo}")

            arq.write(f"Titulo: {noticia.titulo}\n")
            arq.write(f"Data: {noticia.data}\n")
            arq.write(f"Conteudo: {noticia.conteudo}\n")
            arq.write(f"URL: {noticia.url}\n")
            arq.write(f"Fonte: {noticia.fonte}\n")


    except Exception as e:
        print(f"Erro ao coletar {noticia.titulo} {e}")
    
    i+=1

# Executar para COPEL

# for n in noticias:
#     print(f"{i} - {n}")
#     i+=1

# for n in noticia_1:
#     print(f"{i} - {n}")
#     i+=1

