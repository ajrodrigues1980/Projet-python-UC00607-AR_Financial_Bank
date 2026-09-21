import json
import csv
import os
from banco.modelos import Cliente, Conta, Transacao

# Caminhos para a pasta 'dados'
FICHEIRO_CLIENTES = "dados/sistema_bancario.json"
FICHEIRO_MOVIMENTOS = "dados/movimentos.csv"

def garantirPastaDados():
    #verifica e criar a pasta "dados" caso não exista
    if not os.path.exists("dados"):
        os.makedirs("dados")


def guardarDados(bdClientes: dict, bdContas: dict, bdMovimento: list):
    
    garantirPastaDados()
    
    # Guarda os Clientes e Contas num único ficheiro JSON
    dados_json = {}
    for username in bdClientes:
        dados_json[username] = {
            "password": bdClientes[username].password,
            "saldo": bdContas[username].saldo
        }
        
    with open(FICHEIRO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(dados_json, f, ensure_ascii=False, indent=4)
        
    # Guarda Movimentos em CSV
    with open(FICHEIRO_MOVIMENTOS, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        # Cabeçalho tabular
        escritor.writerow(["data_hora", "valor", "userOrigem", "userDestino", "tipo"])
        
        # Escreve cada transação linha a linha
        for t in bdMovimento:
            escritor.writerow([t.data_hora, t.valor, t.userOrigem, t.userDestino, t.tipo])


def carregarDados(bdClientes: dict, bdContas: dict, bdMovimento: list):
    # Carrega os dados de Clientes, Contas e Movimentos do ficheiro JSON e CSV para os dicionários e lista correspondentes.
    # Carrega o conteudo do JSON se ele existir
    if os.path.exists(FICHEIRO_CLIENTES):
        with open(FICHEIRO_CLIENTES, "r", encoding="utf-8") as f:
            dados_json = json.load(f)
            for username, info in dados_json.items():
                bdClientes[username] = Cliente(username=username, password=info["password"])
                bdContas[username] = Conta(username=username, saldo=info["saldo"])
                
    # Carrega o conteúdo do CSV se ele existir
    if os.path.exists(FICHEIRO_MOVIMENTOS):
        with open(FICHEIRO_MOVIMENTOS, "r", encoding="utf-8") as f:
            leitor = csv.reader(f)
            next(leitor)  
            for linha in leitor:
                if linha: 
                    nova_trans = Transacao(
                        data_hora=linha[0],
                        valor=float(linha[1]),
                        userOrigem=linha[2],
                        userDestino=linha[3],
                        tipo=linha[4]
                    )
                    bdMovimento.append(nova_trans)
