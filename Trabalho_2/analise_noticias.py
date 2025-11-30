import pandas as pd
from treinamento_modelo import verificacao_noticias

class Analise():
    def __init__(self):
        self.id = None
        self.data = ""
        self.varia_dia = None
        self.varia_1_dia_antes = None
        self.varia_1_dia_depois = None
        self.varia_2_dias_antes = None
        self.varia_2_dias_depois = None
        self.sentimento_PRE = None
        self.sentimento_POS = None

    def instala(self, id, data, varia_dia, varia_1_dia_antes, varia_1_dia_depois, varia_2_dia_antes, varia_2_dia_depois, sentimento_PRE, sentimento_POS):
        self.id = id
        self.data = data
        self.varia_dia = varia_dia
        self.varia_1_dia_antes = varia_1_dia_antes
        self.varia_1_dia_depois = varia_1_dia_depois
        self.varia_2_dias_antes = varia_2_dia_antes
        self.varia_2_dias_depois = varia_2_dia_depois
        self.sentimento_PRE = sentimento_PRE
        self.sentimento_POS = sentimento_POS


def salvar_noticias_csv(lista_noticias, caminho):
    dados = []
    for d in lista_noticias:
        dados.append({
            "id": d.id,
            "data": d.data,
            "varia_dia": d.varia_dia,
            "varia_1_dia_antes": d.varia_1_dia_antes,
            "varia_1_dia_depois": d.varia_1_dia_depois,
            "varia_2_dias_antes": d.varia_2_dias_antes,
            "varia_2_dias_depois": d.varia_2_dias_depois,
            "sentimento_PRE": d.sentimento_PRE,
            "sentimento_POS": d.sentimento_POS
        })
    
    noticias_csv = pd.DataFrame(dados)
    noticias_csv.to_csv(caminho, index=False, encoding="utf-8")
    print(f"Arquivo salvo em {caminho}\n")

def analisar_empresa(id_empresa):
    df = pd.read_csv(f"historicos_csv/{id_empresa}.SA_historico.csv", parse_dates=["Date"])
    df["Date"] = df["Date"].dt.tz_localize(None) 

    #print(df["Date"])

    noticias = verificacao_noticias(id_empresa)

    lista_dados = []

    for n in noticias:
        a = Analise()

        linha = df.index[df["Date"] == n.data].to_list()
        #print(f"{n.id_noticia} | {linha} | {n.data}\n")

        if linha == []:
            print(f"Data {n.data} (id:{n.id_noticia}) não foi encontrada!\n")
            break
        else:
            i = linha[0]

            try:
                linha_dia = df.iloc[i]
            except:
                linha_dia = None

            try:
                linha_1_anterior = df.iloc[i - 1]
            except:
                linha_1_anterior = None
        
            try:
                linha_1_posterior = df.iloc[i + 1]
            except:
                linha_1_posterior = None 

            try:
                linha_2_anterior = df.iloc[i - 2]
            except:
                linha_2_anterior = None
        
            try:
                linha_2_posterior = df.iloc[i + 2]
            except:
                linha_2_posterior = None 

            #print(f"{linha_dia} |\n {linha_1_anterior} |\n {linha_1_posterior}\n")

            varia_dia = float(linha_dia["Open"]) - float(linha_dia["Close"])
            varia_1_dia_antes = float(linha_1_anterior["Open"]) - float(linha_1_anterior["Close"])
            varia_1_dia_depois = float(linha_1_posterior["Open"]) - float(linha_1_posterior["Close"])
            varia_2_dias_antes = float(linha_2_anterior["Open"]) - float(linha_2_anterior["Close"])
            varia_2_dias_depois = float(linha_2_posterior["Open"]) - float(linha_2_posterior["Close"])

            #print(f"Varia_dia: {varia_dia} | Varia_1_dia_antes: {varia_1_dia_antes} | Varia_1_dia_depois: {varia_1_dia_depois}\n")

            a.instala(n.id_noticia, n.data, varia_dia, varia_1_dia_antes, varia_1_dia_depois, varia_2_dias_antes, varia_2_dias_depois, n.label_PRE, n.label_POS)

            lista_dados.append(a)

    salvar_noticias_csv(lista_dados, f"analises_csv/analise{id_empresa}.csv")
