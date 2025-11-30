import pandas as pd
from leitura_noticias import carregar_noticias
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import KFold, cross_val_score

def treinamento(path):
    # ============================
    # 1. Carregar CSV
    # ============================
    df = pd.read_csv(path)
    
    x = df["conteudo_PRE"]      # texto limpo
    y = df["label"]      # classe: -1, 0, 1 OU 0/1

    # ============================
    # 2. Bag-of-Words + N-gramas
    # ============================
    vectorizer = CountVectorizer(
        max_features=10000,     # limita o dicionário
        ngram_range=(1,2)      # <<< AQUI VOCÊ ESCOLHE 1 OU 2 OU 3
    )

    # ============================
    # 3. Modelo (Naive Bayes)
    # ============================
    modelo = MultinomialNB()

    pipeline = Pipeline([
        ("bow", vectorizer),
        ("clf", modelo)
    ])

    # ============================
    # 4. Avaliação com K-Fold
    # ============================
    kfold = KFold(n_splits=3, shuffle=True, random_state=42)
    scores = cross_val_score(pipeline, x, y, cv=kfold, scoring="accuracy")

    # ============================
    # 5. Treinar modelo final
    # ============================
    pipeline.fit(x, y)

    return pipeline

# ============================
# 6. Função de score (-10 a +10)
# ============================
def score_sentimento(texto, pipeline):
    prob = pipeline.predict_proba(texto)[0]
    # Supondo classes 0 = negativo / 1 = positivo
    score = (prob[1] - prob[0]) * 10
    return round(score)

# Exemplo:
def verificacao_noticias(id_empresa):
    try:
        noticias = carregar_noticias(id_empresa)

        pipeline = treinamento(f"noticias_csv/noticias{id_empresa}.csv")

        #print(f"\n{id_empresa}\n\nPRE:")
        for n in noticias:
            score = score_sentimento([n.conteudo_PRE], pipeline)
            n.label_PRE = score
            #print(f"\nID: {n.id}\nTitulo: {n.titulo}\nScore: {round(score)}")

        #print("\n\nPOS:")
        for n in noticias:
            score = score_sentimento(n.conteudo_POS, pipeline)
            n.label_POS = score
            #print(f"\nID: {n.id}\nTitulo: {n.titulo}\nScore: {round(score)}")

        print(f"Noticias de {id_empresa} foram categorizadas com sucesso.\n")
    
        return noticias
    except Exception as e:
        print(f"ERRO: Nao foi possivel categorizar as noticias de {id_empresa}. {e}.\n")


