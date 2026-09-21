from datetime import datetime
from banco.modelos import Transacao
from banco.excecoes import clienteInexistenteError, saldoInsuficienteError

def consultarSaldo(username: str, bdContas: dict) -> float:
 
    return bdContas[username].saldo


def depositarSaldo(username: str, valor: float, bdContas: dict) -> bool:
  
    if valor <= 0:
        print("Erro: O valor do depósito deve ser maior que zero.")
        return False
    
    bdContas[username].saldo += valor
    print(f"Sucesso: Foram depositados {valor:.2f}€ na conta de {username}.")
    return True

def transferirValor(userOrigem: str, userDestino: str, valor: float, bdContas: dict, bdMovimento: list) -> bool:
    
    # Verifica se o utilizador de destino existe
    if userDestino not in bdContas:
        raise clienteInexistenteError(userDestino)
        
    # Verifica se o valor é positivo
    if valor <= 0:
        print("Erro: O valor da transferência deve ser maior que zero.")
        return False
        
    # Verifica se a conta de origem tem saldo suficiente
    saldoAtual = bdContas[userOrigem].saldo
    if saldoAtual < valor:
        raise saldoInsuficienteError(saldoAtual, valor)
        
    # Executa o movimento financeiro
    bdContas[userOrigem].saldo -= valor
    bdContas[userDestino].saldo += valor
    
    # Regista a transação automaticamente
    agora = datetime.now()
    data_hora_str = agora.strftime("%d/%m/%Y %H:%M:%S")  # Ex: "21/09/2026 23:27:00"
    
    novaTrans = Transacao(
        data_hora=data_hora_str,
        valor=valor,
        userOrigem=userOrigem,
        userDestino=userDestino,
        tipo="Transferência"
    )
    
    bdMovimento.append(novaTrans)  # Adiciona ao histórico tabular (lista)
    
    print(f"Sucesso: Transferência de {valor:.2f}€ para '{userDestino}' realizada!")
    return True