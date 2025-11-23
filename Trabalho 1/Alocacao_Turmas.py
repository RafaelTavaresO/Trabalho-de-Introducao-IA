import time
import json
import random
from collections import deque

class Grafo():
    def __init__(self):
        self.variaveis = ["V1", "V2", "V3", "V4", "V5"]
        self.turmas = []
        self.salas = []
        self.horarios = []
        self.professores = []
        self.dominios = []
        self.vizinhos = []
        self.restricoes = []


def ler_instancia(instancia, restricoes, grafo):
    try:
        with open(instancia, "r") as arquivoI:
            instanciaF = json.load(arquivoI)
            
            grafo.dominios = instanciaF["dominios"]
            grafo.vizinhos = instanciaF["vizinhos"]
            grafo.turmas = instanciaF["turmas"]
            grafo.salas = instanciaF["salas"]
            grafo.horarios = instanciaF["horarios"]

            turma = grafo.turmas
            professores = {}

            for t in turma:
                if turma[t][1] not in professores:
                    professores[turma[t][1]] = []

                professores[turma[t][1]].append(t)


            for p in professores:
                for s in professores[p]:
                    index = professores[p].index(s)
                    if s == "A":
                        professores[p][index] = "V1"
                    elif s == "B":
                        professores[p][index] = "V2"
                    elif s == "C":
                        professores[p][index] = "V3"
            
            grafo.professores = professores

            excluir_v = []
    
            for v in grafo.variaveis:
                if not grafo.dominios[v]:
                    grafo.dominios[v] = None
                    excluir_v.append(v)

        with open(restricoes, "r") as arquivoR:
            r = json.load(arquivoR)
            restricoes = r["restricoes"]
            excluir_r = []

            for c in restricoes:
                vars = []

                for v in restricoes[c]["variaveis"]:
                    if "V" in v:
                        vars.append(v)
                if not any(grafo.dominios[v] == None for v in vars):
                    restricoes[c] = categoriza_restricao(restricoes[c], grafo, c)
                else:
                    restricoes[c] = None
                    excluir_r.append(c)

        for c in excluir_r:    
            if restricoes[c] == None:
                del restricoes[c]

        for v in excluir_v:
            i = grafo.variaveis.index(v)
            del grafo.variaveis[i]
            del grafo.dominios[v]

        grafo.restricoes = restricoes
            
    except FileNotFoundError:
        return 0


def categoriza_restricao(restricao, grafo, c):

    tipo = restricao["tipo"]
    vars = restricao["variaveis"]
    categoria = restricao["categoria"]

    dominio = grafo.dominios
    rest = []

    v1 = vars[0]
    v2 = vars[1]

    if tipo == "IF":

        v3 = vars[2]
        v4 = vars[3]

        variacoes = [
        [v1, v2, v3, v4],
        [v2, v1, v3, v4],
        [v1, v2, v4, v3],
        [v2, v1, v4, v3],
        [v3, v4, v1, v2],
        [v3, v4, v2, v1],
        [v4, v3, v1, v2],
        [v4, v3, v2, v1],
        ]
        i = 0
        
        for v in variacoes:
            restricao = [tipo, v, categoria]
            rest.append(restricao)

            grafo.vizinhos[v[3]].append([v[2], c, i])

            i+=1

        return rest
    
    elif tipo == "capacidade":
        rest.append([tipo, vars, categoria])

        grafo.vizinhos[v1].append([v1, c, 0])

        return rest
    
    
    elif tipo == "diferenca":
        rest.append([tipo, [v1,v2], categoria])
        rest.append([tipo, [v2,v1], categoria])

        grafo.vizinhos[v2].append([v1, c, 0])
        grafo.vizinhos[v1].append([v2, c, 1])

        return rest

    elif tipo == "diferenca_S":
        
        rest.append([tipo, vars, categoria])

        grafo.vizinhos[v1].append([v1, c, 0])

        return rest
    
    elif tipo == "IF_S":

        v3 = vars[2]
        v4 = vars[3]

        variacoes = [
        [v3, v4, v1, v2],
        [v4, v3, v1, v2],
        [v1, v2, v3, v4],
        [v1, v2, v4, v3]
        ]

        i = 0
        
        for v in variacoes:
            restricao = [tipo, v, categoria]
            rest.append(restricao)

            if v1 == v[0]:
                grafo.vizinhos[v[0]].append([v[0], c, i])
            else:
                grafo.vizinhos[v[1]].append([v[0], c, i])

            i+=1

        return rest
    
    elif tipo == "IF_P":

        v3 = vars[2]
        v4 = vars[3]

        variacoes = [
        [v1, v2, v3, v4],
        [v1, v2, v4, v3],
        ]

        i = 0
        
        for v in variacoes:
            restricao = [tipo, v, categoria]
            rest.append(restricao)

            grafo.vizinhos[v[3]].append([v[2], c, i])

            i+=1

        return rest
    
    elif tipo == "SEM_DUPLICIDADE":
        rest.append([tipo, [v1, v2], categoria])

        grafo.vizinhos["V4"].append(["V4", c, 0])
        grafo.vizinhos["V5"].append(["V5", c, 0])   
 
        return rest
    else:
        return None
    
def log_ac3(arq_log, fila, ex):
    try:
        with open(arq_log, "a") as log:
            if ex != 1:
                log.write(f"\n\n\nExecucao {ex}")
            else:
                log.write(f"Execucao {ex}")

            log.write(F"\nFila:")
            j = 0
            for f in fila:
                j+=1
                log.write(f"\nRestricao {j} - {f}")
    except FileNotFoundError:
        print("\n\n\nERRO! A instância não foi aberta!")
        exit(1)
    
def AC3(grafo, log):
    reducoes = []
    restricoes = []
    dominio = grafo.dominios

    for c in grafo.restricoes:
        for n in grafo.restricoes[c]:
            if not (n[0] == 'SEM_DUPLICIDADE' or n[2] == "#S"):
                restricoes.append(n)

    fila = deque(restricoes)
    
    i = 0
    while fila:
        i+=1
        
        log_ac3(log, fila, i)

        restricao = fila.popleft()
        rev, a, removido = revisar(restricao, grafo)
        if rev:
            reducoes.append((a, removido))
            try:
                with open(log, "a") as l:
                    l.write(f"\n\nAlteracao:\n{a} | Dominio - {dominio[a]} | Removido - {removido}\n\nAdicoes:")
            except FileNotFoundError:
                print(f"Log '{log}' não aberto")
                exit(1)
            if not dominio[a]:
                try:
                    with open(log, "a") as l:
                        l.write(f"\n\nFalha - Dominio de {a} esta vazio: {dominio[a]}")
                except FileNotFoundError:
                        print(f"Log '{log}' não aberto")
                        exit(1)

                return False, reducoes  
            for vizinho in grafo.vizinhos[a]:
                rest = grafo.restricoes[vizinho[1]][vizinho[2]]

                if not (rest in fila):
                    try:
                        with open(log, "a") as l:
                            l.write(f"\n{rest}")
                    except FileNotFoundError:
                        print(f"Log '{log}' não aberto")
                        exit(1)
                    
                    fila.append(rest)

    return True, reducoes
    

def revisar(restricao, grafo):
    revisao = False
    volta = "$"
    removido = "$"

    tipo = restricao[0]
    vars = restricao[1]

    dominio = grafo.dominios
    sala = grafo.salas
    turma = grafo.turmas

    v1 = vars[0]
    v2 = vars[1]

    if tipo == "IF":

        v3 = vars[2]
        v4 = vars[3]

        for x in dominio[v1]:
            if all(x == y for y in dominio[v2]):
                for w in dominio[v3]:
                    if not any(w != z for z in dominio[v4]):
                        dominio[v3].remove(w)
                        removido = w
                        revisao = True
                        volta = v3
    
    elif tipo == "capacidade":

        for x in dominio[v1]:
            if not int(sala[x]) >= int(turma[v2][0]):
                dominio[v1].remove(x)
                revisao = True
                volta = v1
                removido = x
    
    elif tipo == "diferenca":
        for x in dominio[v1]:
            if not any(x != y for y in dominio[v2]):
                dominio[v1].remove(x)
                removido = x
                revisao = True
                volta = v1

    elif tipo == "diferenca_S":
        
        for x in dominio[v1]:
            if x != v2:
                dominio[v1].remove(x)
                removido = x
                revisao = True
                volta = v1
    
    elif tipo == "IF_S":

        v3 = vars[2]
        v4 = vars[3]

        if "V" not in v2:
            if all(x == v2 for x in dominio[v1]):
                for y in dominio[v3]: 
                    if all(y == w for w in dominio[v4]): 
                        dominio[v3].remove(y)
                        removido = y
                        revisao = True
                        volta = v3              
        else:
            for x in dominio[v1]:
                if all(x == y for y in dominio[v2]):
                    for w in dominio[v3]:
                        if w == v4:
                            dominio[v3].remove(w)
                            removido = w
                            revisao = True
                            volta = v3
    
    elif tipo == "IF_P":
        v3 = vars[2]
        v4 = vars[3]

        if turma[v1][1] == turma[v2][1]:
            for x in dominio[v3]:
                if not any(x != y for y in dominio[v4]):
                    dominio[v3].remove(x)
                    removido = x
                    revisao = True
                    volta = v3

    return revisao, volta, removido

def verifica_conflitos(var, valor, restricao, grafo):
    conflito = 0

    tipo = restricao[0]
    vars = restricao[1]

    dominio = grafo.dominios

    v1 = vars[0]
    v2 = vars[1]

    if tipo == "IF" or tipo == "IF_P":
        v3 = vars[2]

        for x in dominio[v3]:
            if x == valor:
                conflito += 1
    
    elif tipo == "diferenca" or tipo == "IF_S":
        for x in dominio[v1]:
            if x == valor:
                conflito += 1

    elif tipo == "diferenca_S":
        if valor != v2:
            conflito += 1
    
    return conflito


def ordena_valores_dominios(var, visitados, grafo):
    dominio = grafo.dominios

    def conflitos(valor):
        contador = 0
        for n in grafo.vizinhos[var]:
            if n[0] not in visitados:
                
                rest = grafo.restricoes[n[1]][n[2]]

                if not (rest[0] == "capacidade" or rest[0] == "SEM_DUPLICIDADE"):
                    contador += verifica_conflitos(var, valor, rest, grafo)
        
        if valor == "S1" or valor == "H1":
            contador += 2
        print(valor, contador)

        return contador
    
    return sorted(dominio[var], key=conflitos)

def MRV(grafo, visitados):

    variaveis = []

    for var in grafo.variaveis:
        if var not in visitados:
            variaveis.append(var)

    return min(variaveis, key=lambda var: len(grafo.dominios[var]))

def satisfaz_restricao_hard(grafo, visitados, restricao, v1, v2, valor_1, valor_2):
    tipo = restricao[0]
    vars = restricao[1]

    var1 = vars[0]
    var2 = vars[1]

    if tipo == "IF":

        if var1 in visitados and var2 in visitados:
            if visitados[var1] == visitados[var2]:
                return valor_1 != valor_2
        
        return True

    elif tipo == "capacidade":
        sala, turma = vars

        if v1 == sala and v2 == turma:
            return grafo.salas[valor_1] >= grafo.turmas[valor_2][0]
        
        return True

    elif tipo == "diferenca":
        return valor_1 != valor_2
    
    elif tipo == "IF_S":

        var3 = vars[2]
        var4 = vars[3]

        if v1 == var1:
            if var3 in visitados and var4 in visitados:
                if visitados[var3] == visitados[var4]:
                     return valor_1 != var2
        else:
            if var3 in visitados:
                if visitados[var3] == var4:
                    return  valor_1 != valor_2
        
        return True
    
    elif tipo == "IF_P":
        turma = grafo.turmas

        professores = grafo.professores

        for p in professores:
            for h in grafo.horarios:
                count = 0
                for s in professores[p]:
                    if s in grafo.horarios[h]:
                        count += 1
                if count > 1:
                    return False
        
        return True
    
    elif tipo == "SEM_DUPLICIDADE":
        
        if v1 == "V4" and "V1" in visitados: 
            if not grafo.horarios:
                grafo.horarios[valor_1]["V1"] = visitados["V1"]
                return True
            if all(visitados["V1"] != grafo.horarios[i] for i in grafo.horarios):
                grafo.horarios[valor_1]["V1"] = visitados["V1"]
                return True
            else:
                return False
        elif v1 == "V5" and "V2" in visitados:
            if not grafo.horarios:
                grafo.horarios[valor_2]["V2"] = visitados["V2"]
                return True
            if all(visitados["V2"] != grafo.horarios[i] for i in grafo.horarios):
                grafo.horarios[valor_2]["V2"] = visitados["V2"]
                return True
            else:
                return False

    return True
            
def satisfaz_restricao_soft(restricao, valor, grafo):
    tipo = restricao[0]
    vars = restricao[1]

    var1 = vars[0]
    var2 = vars[1]

    custo = 0

    if tipo == "diferenca_S":
        if valor != var2:
            custo = 5
        return custo
        

def consistencia(var, valor, visistados, grafo):
    custo = 0
    
    for vizinho, restricao_id, restricao_pos in grafo.vizinhos[var]:
        if vizinho in visistados:
            valor_vizinho = visistados[vizinho]

            restricao = grafo.restricoes[restricao_id][restricao_pos]

            if restricao[2] == "#S":
                custo = satisfaz_restricao_soft(restricao, valor, grafo)
            else:
                if not satisfaz_restricao_hard(grafo, visistados, restricao, var, vizinho, valor, valor_vizinho):
                    return False, 0 
        elif vizinho == var:
            valor_vizinho = valor
            restricao = grafo.restricoes[restricao_id][restricao_pos]

            if restricao[2] == "#S":
                custo = satisfaz_restricao_soft(restricao, valor, grafo)
            else:
                if not satisfaz_restricao_hard(grafo, visistados, restricao, var, vizinho, valor, valor_vizinho):
                    return False, 0 
            
    return True, custo

def Busca_Em_Profundidade(grafo, visitados, custo, mrv, lcv, nos, falhas, ac3):
    nos += 1

    if len(visitados) == len(grafo.variaveis):
        return visitados, custo, nos, falhas

    if mrv:
        var = MRV(grafo, visitados)
    else:
        var = random.choice([x for x in grafo.variaveis if x not in visitados])
        
    if lcv:
        possibilidades = ordena_valores_dominios(var, visitados, grafo)
    else:
        possibilidades = grafo.dominios[var]

    for valor in possibilidades:
        consistente, custo_a = consistencia(var, valor, visitados, grafo)

        if consistente:
            visitados[var] = valor
            custo += custo_a

            if valor == "Lab1":
                grafo.horarios["H1"][var] = valor 
            
            if ac3[0]:
                backup_dominio = grafo.dominios[var]

                grafo.dominios[var] = [valor] 

                ok, reducoes= AC3(grafo, ac3[1])
            else:
                ok = True
                reducoes = []

            if ok:
                resultado, custo, nos, falhas = Busca_Em_Profundidade(grafo, visitados, custo, mrv, lcv, nos, falhas, ac3) 

                if resultado:

                    return resultado, custo, nos, falhas
                
            if ac3[0]:
                for var_cortada, valor_cortado in reducoes:
                    grafo.dominios[var_cortada].append(valor_cortado)

                grafo.dominios[var] = backup_dominio

            del visitados[var]
            if var in grafo.horarios:
                del grafo.horarios[var]
            custo -= custo_a
            falhas +=1

    falhas +=1


    return None, custo, nos, falhas

def executador(instanca, restricoes, log_busca, log_AC3, mrv, lcv, ac3):
    grafo = Grafo()
    visitados = {}
    nos, falhas = 0, 0
    
    try:
        with open(log_busca, "a") as l:
            if (not mrv) or (not lcv):
                if (not mrv) and (not lcv):
                    l.write(f"\nSem MRV e LCV:\n")
                    
                elif not mrv:
                    l.write(f"\nSem MRV e com LCV:\n")
                    
                else: 
                    l.write(f"\nSem LCV e com MRV:\n")
            else:
                l.write(f"\nCom MRV e LCV:\n")

    except FileNotFoundError:
        print(f"Log {log_busca} não aberto")

    start_time = time.time()

    ler_instancia(instanca, restricoes, grafo)

    if ac3:
        AC3(grafo, log_AC3)
    else:

        try:
            with open(log_busca, "a") as l:
                l.write(f"\nSem AC-3\n")

        except FileNotFoundError:
            print(f"Log {log_busca} não aberto")

    solucao, custo, nos, falhas = Busca_Em_Profundidade(grafo, visitados, 0, mrv, lcv, nos, falhas, [ac3, log_AC3])

    end_time = time.time()
    if not solucao:
        print("\nSem solução")
    else:    
        print(f"Solucao:")

        for s in solucao:
            print(f"   {s}: {solucao[s]}")

        print(f"Nos: {nos}\nFalhas: {falhas}\n\nTempo {((end_time - start_time)*1000):.2f} ms\nCusto = {custo}")
        
    try:
        with open(log_busca, "a") as l:
            if not solucao:
                l.write("\n\nSem solucao.")
            else:
                l.write(f"\nSolucao:")

                for s in solucao:
                    l.write(f"\n   {s}: {solucao[s]}")

                l.write(f"\n\nNos: {nos}\nFalhas: {falhas}\n\nTempo {((end_time - start_time)*1000):.2f} ms\nCusto = {custo}\n\n")
    except FileNotFoundError:
        print(f"Log {log_busca} não aberto")

def main():
    random.seed(time.time())

    execucoes = {
        "Facil":   ["instancias/instanciaFacil.json", "restricoes/restricoesFacil.json", "logs_busca/log_busca_Facil.txt", "logs_ac3/log_ac3_Facil.txt"],
        "Medio":   ["instancias/instanciaMedia.json", "restricoes/restricoesMedia.json", "logs_busca/log_busca_Media.txt", "logs_ac3/log_ac3_Media.txt"],
        "Dificil": ["instancias/instanciaDificil.json", "restricoes/restricoesDificil.json", "logs_busca/log_busca_Dificil.txt", "logs_ac3/log_ac3_Dificil.txt"]
    }

    execucao = 0

    ac3 = 1
    mrv = 0
    lcv = 0

    for e in execucoes:
        print(f"\nInstancia {e}")

        try:
            with open(execucoes[e][2], "w") as l:
                l.write(f"Instancia {e}\n\n")
        except FileNotFoundError:
            print("Log não aberto")
            exit(1)            

        try:
            with open(execucoes[e][3], "w") as l:
                l.write(f"\n\Execucao {execucao}:\n")

        except FileNotFoundError:
            print("Log não aberto")
            exit(1)

        executador(execucoes[e][0], execucoes[e][1], execucoes[e][2], execucoes[e][3], mrv, lcv, ac3)
        execucao += 1

    mrv = 1
    lcv = 0

    for e in execucoes:
        print(f"\nInstancia {e}")
 
        try:
            with open(execucoes[e][3], "w") as l:
                l.write(f"\n\Execucao {execucao}:\n")

        except FileNotFoundError:
            print("Log não aberto")
            exit(1)

        executador(execucoes[e][0], execucoes[e][1], execucoes[e][2], execucoes[e][3], mrv, lcv, ac3)
        execucao += 1

    mrv = 0
    lcv = 1

    for e in execucoes:
        print(f"\nInstancia {e}")

        try:
            with open(execucoes[e][3], "w") as l:
                l.write(f"\n\Execucao {execucao}:\n")

        except FileNotFoundError:
            print("Log não aberto")
            exit(1)

        executador(execucoes[e][0], execucoes[e][1], execucoes[e][2], execucoes[e][3], mrv, lcv, ac3)
        execucao += 1

    mrv = 1
    lcv = 1

    for e in execucoes:
        print(f"\nInstancia {e}")

        try:
            with open(execucoes[e][3], "a") as l:
                l.write(f"\n\nExecucao {execucao}:\n")
        except FileNotFoundError:
            print("Log não aberto")
            exit(1)

        executador(execucoes[e][0], execucoes[e][1], execucoes[e][2], execucoes[e][3], mrv, lcv, ac3)
        execucao += 1

    ac3 = 0
    mrv = 0
    lcv = 0

    for e in execucoes:
        print(f"\nInstancia {e}")
        
        executador(execucoes[e][0], execucoes[e][1], execucoes[e][2], execucoes[e][3], mrv, lcv, ac3)


if __name__ == "__main__":
    main()