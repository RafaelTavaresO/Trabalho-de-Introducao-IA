import yfinance as finance
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from unidecode import unidecode
import spacy

mes = {
    "jan": "01",
    "fev": "02",
    "mar": "03",
    "abr": "04",
    "mai": "05",
    "jun": "06",
    "jul": "07",
    "ago": "08",
    "set": "09",
    "out": "10",
    "nov": "11",
    "dez": "12",
    }

nlp = spacy.load("pt_core_news_sm")

stopwords_pt = set(stopwords.words("portuguese"))

STOPWORDS_EXTRA = {
    "ser", "estar", "ter", "haver", "fazer", 
    "a", "o", "as", "os", "de", "da", "do",
    "em", "para", "por", "um", "uma", "é",
}

STOPWORDS = set(nlp.Defaults.stop_words)

class Noticia():
    def __init__(self):
        self.id_noticia = None
        self.titulo = ""
        self.data = ""
        self.conteudo_PRE = ""
        self.conteudo_POS = ""
        self.url = ""
        self.fonte = ""
        self.label = None
        self.label_PRE = None
        self.label_POS = None

    def carrega_noticia(self, titulo, data, conteudo_PRE, conteudo_POS , url):
        self.titulo = titulo
        self.data = data
        self.conteudo_PRE = conteudo_PRE
        self.conteudo_POS = conteudo_POS
        self.url = url  

def converte_data_infomoney(data):
    data_str = data
    try:
        dt = datetime.strptime(data_str, "%d/%m/%Y %Hh%M")
        data_formatada = dt.strftime("%Y-%m-%d")

    except:
        for m in mes:
            dt_str = re.sub(f"{m}", f"{mes[m]}", data_str)
            if dt_str != data_str:
                break
        
        dt = datetime.strptime(dt_str, "%d %m %Y %Hh%M")
        data_formatada = dt.strftime("%Y-%m-%d")

    return data_formatada

def limpar_texto(texto):
    texto = unidecode(texto.lower())

    # 2. Manter apenas letras e números
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    # 3. Lematização com spaCy
    doc = nlp(texto)

    tokens = []
    for token in doc:
        lemma = token.lemma_

        # manter apenas palavras alfabeticas
        if not lemma.isalpha():
            continue
        
        # tirar stopwords
        if lemma in STOPWORDS:
            continue
        
        # descartar tokens muito curtos
        if len(lemma) < 2:
            continue
        
        tokens.append(lemma)

    return tokens

def limpar_lista_textos(lista_textos):
    palavras = []
    for trecho in lista_textos:
        palavras.extend(limpar_texto(trecho))
    return palavras

    
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
    article = soup.find("article", class_=lambda c: c and "im-article" in c)
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

            if tag.name == "p":
                texto = "".join(tag.find_all(string=True, recursive=False)).strip()
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
    a.carrega_noticia(titulo, data, conteudo, texto, noticia.url)
    a.id_noticia = noticia.id_noticia
    a.fonte = noticia.fonte
    a.label = noticia.label

    return a

def carregar_links(path):
    links = []
    with open(path, "r", encoding="utf-8") as f:
        for linha in f:
            if linha != "\n":
                partes = linha.strip().split(" - ")

                indice = partes[0]
                link = partes[1]
                label = int(re.sub(r"label: ", "", partes[2]))

                if link:
                    a = Noticia()
                    a.id_noticia = indice
                    a.url = link
                    a.fonte = "InfoMoney"
                    a.label = label
                    links.append(a)
    return links

def processar_empresa(ticker_str):
    ticker = finance.Ticker(ticker_str)

    dados = ticker.history(period="1y")
    dados.to_csv(f"historicos_csv/{ticker_str}_historico.csv")

    return dados

def salvar_noticias_csv(lista_noticias, caminho, empresa):
    dados = []
    for n in lista_noticias:
        dados.append({
            "empresa": empresa,
            "id": n.id_noticia,
            "titulo": n.titulo,
            "data": n.data,
            "conteudo_PRE": n.conteudo_PRE,    # dependendo do nome: conteudo, texto, etc.
            "conteudo_POS": n.conteudo_POS,  # dependendo do nome: conteudo, texto, etc.
            "url": n.url,
            "fonte": n.fonte,
            "label": n.label
        })
    
    noticias_csv = pd.DataFrame(dados)
    noticias_csv.to_csv(caminho, index=False, encoding="utf-8")
    print(f"Arquivo salvo em {caminho}\n")

def carregar_noticias(id_empresa):

    path=f"urls/noticias-{id_empresa}.txt"

    # Exemplo de uso
    noticias = carregar_links(path)

    processar_empresa(f"{id_empresa}.SA")

    # for n in noticia_1:
    #     noticias.append(n)

    noticias_dados = []

    for noticia in noticias:
        try: 
            noticia = scrape_infomoney(noticia)
            noticias_dados.append(noticia)

        except Exception as e:
            print(f"Erro ao coletar {noticia.titulo} {e}")
        
    salvar_noticias_csv(noticias_dados, f"noticias_csv/noticias{id_empresa}.csv", id_empresa)
    return noticias_dados


