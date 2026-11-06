"""Operações de conta: saldo, depósitos, levantamentos, transferências, retorno e relatório."""

from datetime import datetime
from banco.modelos import Transacao
from banco.excecoes import (
    clienteInexistenteError,
    saldoInsuficienteError,
    ValorInvalidoError,
)

# Cada mês é uma chamada recursiva. 600 meses são 50 anos e ficam
# abaixo do limite de recursão do Python, cerca de 1000 chamadas.
TAXA_JUROS_MAXIMA = 100
MESES_MINIMOS = 1
MESES_MAXIMOS = 600

def consultarSaldo(username: str, bdContas: dict) -> float:
    """Devolve o saldo atual da conta do utilizador.

    Args:
        username: cliente autenticado.
        bdContas: contas existentes, indexadas por username.

    Returns:
        O saldo atual, em euros.
    """
    return bdContas[username].saldo


def depositarSaldo(username: str, valor: float, bdContas: dict, bdMovimento: list) -> bool:
    """Aumenta o saldo e regista o depósito no histórico.

    Args:
        username: cliente que deposita.
        valor: montante em euros, maior que zero.
        bdContas: contas existentes, indexadas por username.
        bdMovimento: histórico onde o depósito fica registado.

    Returns:
        True quando o saldo e o histórico foram actualizados.

    Raises:
        ValorInvalidoError: o valor não é maior que zero.
    """
    if valor <= 0:
        raise ValorInvalidoError("Erro: O valor do depósito deve ser maior que zero.")
    
    bdContas[username].saldo += valor

    # O depósito também entra no extrato (até agora só as transferências eram guardadas)
    agora = datetime.now()
    data_hora_str = agora.strftime("%d/%m/%Y %H:%M:%S")
    novaTrans = Transacao(
        data_hora=data_hora_str,
        valor=valor,
        userOrigem=username,
        userDestino=username,
        tipo="Depósito"
    )
    bdMovimento.append(novaTrans)

    print(f"Sucesso: Foram depositados {valor:.2f}€ na conta de {username}.")
    return True


def levantarSaldo(username: str, valor: float, bdContas: dict, bdMovimento: list) -> bool:
    """Diminui o saldo e regista o levantamento no histórico.

    Args:
        username: cliente que levanta.
        valor: montante em euros, maior que zero.
        bdContas: contas existentes, indexadas por username.
        bdMovimento: histórico onde o levantamento fica registado.

    Returns:
        True quando o saldo e o histórico foram actualizados.

    Raises:
        ValorInvalidoError: o valor não é maior que zero.
        saldoInsuficienteError: a conta não tem saldo para o valor pedido.
    """
    if valor <= 0:
        raise ValorInvalidoError("Erro: O valor do levantamento deve ser maior que zero.")

    saldo_atual = bdContas[username].saldo
    if saldo_atual < valor:
        raise saldoInsuficienteError(saldo_atual, valor)

    bdContas[username].saldo -= valor

    agora = datetime.now()
    data_hora_str = agora.strftime("%d/%m/%Y %H:%M:%S")
    novo_movimento = Transacao(
        data_hora=data_hora_str,
        valor=valor,
        userOrigem=username,
        userDestino=username,
        tipo="Levantamento"
    )
    bdMovimento.append(novo_movimento)

    print(f"Sucesso: Foram levantados {valor:.2f}€ da conta de {username}.")
    return True


def calculaValorFuturo(saldo: float, taxa_juros: float, meses: int) -> float:
    """Calcula o saldo após juros compostos, mês a mês, de forma recursiva.

    A taxa é uma percentagem aplicada uma vez por mês.
    O caso base é meses == 0.

    Args:
        saldo: valor atual da conta, em euros.
        taxa_juros: percentagem mensal, positiva ou negativa.
        meses: quantos meses faltam aplicar.

    Returns:
        O saldo depois de aplicados todos os meses.
    """
    # Caso base: sem meses por aplicar, o saldo mantém-se e a recursão pára.
    if meses == 0:
        return saldo

    # Caso recursivo: aplica a taxa deste mês e aproxima-se do caso base.
    saldo_apos_mes = saldo * (1 + taxa_juros / 100)
    return calculaValorFuturo(saldo_apos_mes, taxa_juros, meses - 1)


def consultarRetorno(saldo: float) -> None:
    """Pede a taxa e os meses, valida os limites e mostra o valor futuro.

    O saldo real da conta não é alterado: é só uma simulação.

    Args:
        saldo: saldo atual sobre o qual o juro é calculado.
    """
    try:
        meses = int(input("Prazo a calcular, em meses (1 a 600, até 50 anos): ").strip())
        taxa_juros = float(input("Introduza a taxa de juro em % (-100 a 100): ").strip())
    except ValueError:
        print("Erro: Introduza valores numéricos.")
        return

    # O enunciado aceita taxa negativa, desde que o valor absoluto não passe de 100.
    if abs(taxa_juros) > TAXA_JUROS_MAXIMA:
        print(f"Erro: A taxa de juro deve estar entre -{TAXA_JUROS_MAXIMA} e {TAXA_JUROS_MAXIMA}.")
        return

    # O prazo é positivo e cabe na recursão: 1 a 600 meses.
    if not (MESES_MINIMOS <= meses <= MESES_MAXIMOS):
        print(f"Erro: O prazo deve estar entre {MESES_MINIMOS} e {MESES_MAXIMOS} meses (50 anos).")
        return

    valor_futuro = calculaValorFuturo(saldo, taxa_juros, meses)
    if meses % 12 == 0:
        prazo = f"{meses} meses ({meses // 12} anos)"
    else:
        prazo = f"{meses} meses"
    print(f"Valor futuro ao fim de {prazo}: {valor_futuro:.2f}€")
    print(f"Retorno: {valor_futuro - saldo:.2f}€")


def consultarMovimentos(username: str, bdMovimento: list) -> list:
    """Devolve os movimentos em que o cliente é origem ou destino.

    Args:
        username: cliente autenticado.
        bdMovimento: histórico completo do sistema.

    Returns:
        Lista com depósitos, levantamentos e transferências dessa conta.
    """
    movimentos = []
    for t in bdMovimento:
        if t.userOrigem == username or t.userDestino == username:
            movimentos.append(t)
    return movimentos

def transferirValor(user_origem: str, user_destino: str, valor: float, bd_contas: dict, bd_movimento: list) -> bool:
    """Move saldo da conta de origem para a de destino e regista a transferência.

    Args:
        user_origem: username de quem envia.
        user_destino: username de quem recebe.
        valor: montante a transferir, em euros.
        bd_contas: contas existentes, indexadas por username.
        bd_movimento: histórico onde a transferência fica registada.

    Returns:
        True quando o saldo das duas contas e o histórico foram actualizados.

    Raises:
        clienteInexistenteError: a conta de destino não existe.
        ValorInvalidoError: o valor não é positivo, ou a origem e o destino são o mesmo cliente.
        saldoInsuficienteError: a origem não tem saldo para o valor pedido.
    """
    if user_destino not in bd_contas:
        raise clienteInexistenteError(user_destino)

    # A mesma conta a enviar e a receber não muda o saldo e só criaria um movimento falso.
    if user_origem == user_destino:
        raise ValorInvalidoError(
            "O cliente de destino é o mesmo, por favor inserir novo destinatário para a transferência"
        )

    if valor <= 0:
        raise ValorInvalidoError("Erro: O valor da transferência deve ser maior que zero.")

    # O saldo é lido antes de subtrair, para a excepção mostrar o valor real.
    saldo_atual = bd_contas[user_origem].saldo
    if saldo_atual < valor:
        raise saldoInsuficienteError(saldo_atual, valor)

    bd_contas[user_origem].saldo -= valor
    bd_contas[user_destino].saldo += valor

    agora = datetime.now()
    data_hora_str = agora.strftime("%d/%m/%Y %H:%M:%S")

    nova_transacao = Transacao(
        data_hora=data_hora_str,
        valor=valor,
        userOrigem=user_origem,
        userDestino=user_destino,
        tipo="Transferência"
    )
    bd_movimento.append(nova_transacao)

    print(f"Sucesso: Transferência de {valor:.2f}€ para '{user_destino}' realizada!")
    return True


def recolherSaldos(bdContas: dict, fila) -> None:
    """Envia para a fila o saldo de cada conta. Corre num processo próprio.

    Args:
        bdContas: contas existentes, indexadas por username.
        fila: fila do processo, onde o dicionário de saldos é colocado.
    """
    saldos = {}
    for username, conta in bdContas.items():
        saldos[username] = conta.saldo
    fila.put(saldos)


def recolherNumeroTransferencias(bdMovimento: list, fila) -> None:
    """Envia para a fila quantas transferências envolvem cada utilizador.

    Depósitos e levantamentos não entram na contagem.

    Args:
        bdMovimento: histórico completo do sistema.
        fila: fila do processo, onde o dicionário de totais é colocado.
    """
    totais = {}
    for transacao in bdMovimento:
        if transacao.tipo != "Transferência":
            continue
        # Origem e destino contam uma vez cada, na respectiva conta.
        envolvidos = {transacao.userOrigem, transacao.userDestino}
        for username in envolvidos:
            totais[username] = totais.get(username, 0) + 1
    fila.put(totais)


def ordenarLinhasPorSaldo(linhas: list) -> list:
    """Ordena as linhas do relatório pelo saldo, do maior para o menor, com Selection Sort.

    Args:
        linhas: cada linha tem username, número de transferências e saldo.

    Returns:
        Uma lista nova, ordenada. A lista recebida não é alterada.
    """
    ordenadas = list(linhas)
    n = len(ordenadas)
    for i in range(n - 1):
        indice_escolhido = i
        for j in range(i + 1, n):
            if ordenadas[j]["saldo"] > ordenadas[indice_escolhido]["saldo"]:
                indice_escolhido = j
        if indice_escolhido != i:
            ordenadas[i], ordenadas[indice_escolhido] = (
                ordenadas[indice_escolhido],
                ordenadas[i],
            )
    return ordenadas


def mostrarRelatorioSistema(linhas: list) -> None:
    """Imprime a tabela de contas pedida no projeto."""
    print("\n[ RELATÓRIO DO SISTEMA ]")
    if not linhas:
        print("Não existem contas.")
        return
    print(f"{'Username':<20} {'Transferências':>16} {'Saldo':>12}")
    print("-" * 52)
    for linha in linhas:
        print(
            f"{linha['username']:<20} {linha['transferencias']:>16} "
            f"{linha['saldo']:>10.2f}€"
        )


def gerarRelatorioContas(bdContas: dict) -> None:
    """Imprime quem tem mais saldo, quem tem menos e a soma de todos os saldos."""
    if not bdContas:
        print("Relatório de contas: não existem contas.")
        return

    maior_saldo = None
    menor_saldo = None
    com_mais = []
    com_menos = []
    saldo_total = 0.0

    # Um empate no maior ou no menor saldo inclui todos os utilizadores com esse valor.
    for username, conta in bdContas.items():
        saldo = conta.saldo
        saldo_total += saldo
        if maior_saldo is None or saldo > maior_saldo:
            maior_saldo = saldo
            com_mais = [username]
        elif saldo == maior_saldo:
            com_mais.append(username)
        if menor_saldo is None or saldo < menor_saldo:
            menor_saldo = saldo
            com_menos = [username]
        elif saldo == menor_saldo:
            com_menos.append(username)

    print("\n[ RELATÓRIO DE CONTAS ]")
    print(f"Soma de todos os saldos: {saldo_total:.2f}€")
    print("Utilizadores com maior saldo:")
    for username in com_mais:
        print(f"- {username}: {maior_saldo:.2f}€")
    print("Utilizadores com menor saldo:")
    for username in com_menos:
        print(f"- {username}: {menor_saldo:.2f}€")


def gerarRelatorioTransferencias(bdMovimento: list) -> None:
    """Imprime quem mais recebeu, quem mais enviou e a soma do dinheiro transferido."""
    recebido = {}
    enviado = {}
    total_transferido = 0.0

    for transacao in bdMovimento:
        if transacao.tipo != "Transferência":
            continue
        total_transferido += transacao.valor
        recebido[transacao.userDestino] = recebido.get(transacao.userDestino, 0.0) + transacao.valor
        enviado[transacao.userOrigem] = enviado.get(transacao.userOrigem, 0.0) + transacao.valor

    print("\n[ RELATÓRIO DE TRANSFERÊNCIAS ]")
    if not recebido:
        print("Ainda não existem transferências.")
        return

    mais_recebido = max(recebido.values())
    mais_enviado = max(enviado.values())
    print(f"Soma de todo o dinheiro transferido: {total_transferido:.2f}€")
    print("Quem mais recebeu:")
    for username, valor in recebido.items():
        if valor == mais_recebido:
            print(f"- {username}: {valor:.2f}€")
    print("Quem mais enviou:")
    for username, valor in enviado.items():
        if valor == mais_enviado:
            print(f"- {username}: {valor:.2f}€")


def ordenarPorData(transferencias: list, decrescente: bool) -> list:
    """Ordena transferências por data com Bubble Sort."""
    ordenadas = list(transferencias)
    n = len(ordenadas)

    # Cada passagem coloca uma data na posição final, comparando vizinhos.
    for i in range(n - 1):
        for j in range(n - 1 - i):
            data_atual = datetime.strptime(ordenadas[j].data_hora, "%d/%m/%Y %H:%M:%S")
            data_seguinte = datetime.strptime(ordenadas[j + 1].data_hora, "%d/%m/%Y %H:%M:%S")
            if decrescente:
                fora_de_ordem = data_atual < data_seguinte
            else:
                fora_de_ordem = data_atual > data_seguinte
            if fora_de_ordem:
                ordenadas[j], ordenadas[j + 1] = ordenadas[j + 1], ordenadas[j]
    return ordenadas


def ordenarPorValor(transferencias: list, decrescente: bool) -> list:
    """Ordena transferências por valor com Selection Sort."""
    ordenadas = list(transferencias)
    n = len(ordenadas)

    # Em cada posição i, procura o valor que deve ficar aí e troca uma vez.
    for i in range(n - 1):
        indice_escolhido = i
        for j in range(i + 1, n):
            if decrescente:
                esta_melhor = ordenadas[j].valor > ordenadas[indice_escolhido].valor
            else:
                esta_melhor = ordenadas[j].valor < ordenadas[indice_escolhido].valor
            if esta_melhor:
                indice_escolhido = j
        if indice_escolhido != i:
            ordenadas[i], ordenadas[indice_escolhido] = (
                ordenadas[indice_escolhido],
                ordenadas[i],
            )
    return ordenadas


def pesquisarPorValor(transferencias: list, valor: float) -> tuple:
    """Pesquisa sequencial: percorre a lista até ao fim e junta todos os valores iguais.

    Args:
        transferencias: transferências do utilizador autenticado.
        valor: montante procurado, em euros.

    Returns:
        As transferências encontradas e o número de comparações.
    """
    encontradas = []
    comparacoes = 0
    for transacao in transferencias:
        comparacoes += 1
        if round(transacao.valor, 2) == round(valor, 2):
            encontradas.append(transacao)
    return encontradas, comparacoes


def pesquisarPorData(transferencias: list, data_procurada) -> tuple:
    """Pesquisa binária por dia. Ordena primeiro por data, porque a lista tem de estar ordenada.

    Args:
        transferencias: transferências do utilizador autenticado.
        data_procurada: dia a procurar, sem hora.

    Returns:
        As transferências desse dia e o número de comparações da pesquisa.
    """
    ordenadas = ordenarPorData(transferencias, decrescente=False)
    comparacoes = 0
    inicio = 0
    fim = len(ordenadas) - 1
    encontrado = -1

    # Cada passo olha para o meio e descarta a metade onde a data não pode estar.
    while inicio <= fim:
        meio = (inicio + fim) // 2
        data_meio = datetime.strptime(
            ordenadas[meio].data_hora, "%d/%m/%Y %H:%M:%S"
        ).date()
        comparacoes += 1
        if data_meio == data_procurada:
            encontrado = meio
            break
        if data_meio < data_procurada:
            inicio = meio + 1
        else:
            fim = meio - 1

    if encontrado == -1:
        return [], comparacoes

    # O mesmo dia pode aparecer várias vezes; alarga a partir do índice encontrado.
    primeiro = encontrado
    while primeiro > 0:
        data_anterior = datetime.strptime(
            ordenadas[primeiro - 1].data_hora, "%d/%m/%Y %H:%M:%S"
        ).date()
        if data_anterior != data_procurada:
            break
        primeiro -= 1

    ultimo = encontrado
    while ultimo + 1 < len(ordenadas):
        data_seguinte = datetime.strptime(
            ordenadas[ultimo + 1].data_hora, "%d/%m/%Y %H:%M:%S"
        ).date()
        if data_seguinte != data_procurada:
            break
        ultimo += 1

    return ordenadas[primeiro:ultimo + 1], comparacoes


def mostrarTransferencias(transferencias: list) -> None:
    """Imprime a tabela de transferências já filtrada."""
    print(f"{'Data':<20} {'Valor':>10}  {'Origem':<16} {'Destino':<16}")
    print("-" * 66)
    for transacao in transferencias:
        print(
            f"{transacao.data_hora:<20} {transacao.valor:>10.2f}€ "
            f"{transacao.userOrigem:<16} {transacao.userDestino:<16}"
        )


def consultarTransferencias(username: str, bdMovimento: list) -> None:
    """Mostra as transferências do utilizador, ordenadas ou pesquisadas."""
    transferencias = []
    for transacao in bdMovimento:
        if transacao.tipo != "Transferência":
            continue
        if transacao.userOrigem == username or transacao.userDestino == username:
            transferencias.append(transacao)

    if not transferencias:
        print("Não existem transferências para este utilizador.")
        return

    print("1. Ordenar por data (Bubble Sort)")
    print("2. Ordenar por valor (Selection Sort)")
    print("3. Pesquisar por valor (Pesquisa sequencial)")
    print("4. Pesquisar por data (Pesquisa binária)")
    opcao = input("Escolha uma opção: ").strip()

    if opcao in ("1", "2"):
        ordem = input("Ordem crescente ou decrescente? (c/d): ").strip().lower()
        if ordem not in ("c", "d"):
            print("Erro: Escolha 'c' para crescente ou 'd' para decrescente.")
            return
        decrescente = ordem == "d"
        if opcao == "1":
            ordenadas = ordenarPorData(transferencias, decrescente)
        else:
            ordenadas = ordenarPorValor(transferencias, decrescente)
        mostrarTransferencias(ordenadas)
        return

    if opcao == "3":
        try:
            valor = float(input("Introduza o valor a pesquisar (€): ").strip())
        except ValueError:
            print("Erro: Introduza um número válido para o valor.")
            return
        encontradas, comparacoes = pesquisarPorValor(transferencias, valor)
        if not encontradas:
            print("Não existem transferências com esse valor.")
        else:
            mostrarTransferencias(encontradas)
        print(f"Comparações: {comparacoes}")
        return

    if opcao == "4":
        while True:
            texto = input("Introduza a data (dd/mm/aaaa): ").strip()
            if texto == "0":
                return
            try:
                data_procurada = datetime.strptime(texto, "%d/%m/%Y").date()
                break
            except ValueError:
                print("Erro: Introduza a data no formato dd/mm/aaaa.")
                print("Volte a Introduzir a data no formato pedido, 0 - Voltar ao menu anterior")
        encontradas, comparacoes = pesquisarPorData(transferencias, data_procurada)
        if not encontradas:
            print("Não existem transferências nessa data.")
        else:
            mostrarTransferencias(encontradas)
        print(f"Comparações: {comparacoes}")
        return

    print("Opção inválida! Tente novamente.")