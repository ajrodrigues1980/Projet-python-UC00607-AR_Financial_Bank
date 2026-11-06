"""Programa principal do EISNT Bank: menus, validações e arranque dos processos do relatório."""

import os
import multiprocessing
# Titulo Bonito com pyfiglet :)
try:
    import pyfiglet
    TEM_FIGLET = True
except ImportError:
    TEM_FIGLET = False

# Importação dos módulos
from banco.clientes import criarCliente, fazerLogin
from banco.contas import (
    consultarSaldo,
    depositarSaldo,
    levantarSaldo,
    transferirValor,
    consultarMovimentos,
    consultarRetorno,
    recolherSaldos,
    recolherNumeroTransferencias,
    ordenarLinhasPorSaldo,
    mostrarRelatorioSistema,
    consultarTransferencias,
)
from banco.guardarDados import carregarDados, guardarDados
from banco.excecoes import (
    clienteJaExisteError,
    clienteInexistenteError,
    saldoInsuficienteError,
    PasswordInvalidaError,
    ValorInvalidoError,
)

# Inicializar as "Bases de Dados" na memória RAM
bdClientes = {}
bdContas = {}
bdMovimento = []

def limpar_ecra():
    """Limpa o ecrã da consola, no Windows ou noutro sistema."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Arranca o banco, carrega os dados e gere os menus até o utilizador sair."""
    # Carrega dados guardados no arranque do sistema
    carregarDados(bdClientes, bdContas, bdMovimento)
    
    limpar_ecra()
    if TEM_FIGLET:
        pyfiglet.print_figlet("EISNT Bank", font="slant")
    else:
        print("=" * 30)
        print("          EISNT BANK          ")
        print("=" * 30)

    userAutenticado = None  # Guarda o username de quem fez login

    # LOOP PRINCIPAL DO PROGRAMA
    while True:
        if not userAutenticado:
            # MENU INICIAL
            print("\n--- MENU PRINCIPAL ---")
            print("1. Criar Conta Cliente")
            print("2. Entrar (Login)")
            print("3. Sair do Programa")
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                print("\n[ REGISTAR NOVO CLIENTE ]")
                username = input("Username pretendido: ").strip()
                voltar = False

                # O username duplicado é verificado já aqui, antes de pedir a password.
                while True:
                    try:
                        if username in bdClientes:
                            raise clienteJaExisteError(username)
                    except clienteJaExisteError:
                        print("Utilizador já existe, volte a tentar")
                        print("0 - Voltar ao menu anterior")
                        username = input().strip()
                        if username == "0":
                            voltar = True
                            break
                        continue
                    break

                if not voltar:
                    password = input("Password (6-10 chars, 1 letra, 1 número): ").strip()
                    # Só cria o cliente depois de a password passar na validação.
                    while True:
                        try:
                            criarCliente(username, password, bdClientes, bdContas)
                            break
                        except clienteJaExisteError:
                            print("Utilizador já existe, volte a tentar")
                            break
                        except PasswordInvalidaError as e:
                            print(e)
                            print("0 - Voltar ao menu anterior")
                            password = input().strip()
                            if password == "0":
                                break
                    
            elif opcao == "2":
                print("\n[ ENTRAR NO SISTEMA ]")
                username = input("Username: ").strip()
                voltar = False

                # O username é verificado já aqui, antes de pedir a password.
                while True:
                    try:
                        if username not in bdClientes:
                            raise clienteInexistenteError(username)
                    except clienteInexistenteError:
                        print("Utilizador não existe, volte a tentar")
                        print("0 - Voltar ao menu anterior")
                        username = input().strip()
                        if username == "0":
                            voltar = True
                            break
                        continue
                    break

                if not voltar:
                    password = input("Password: ").strip()
                    while True:
                        try:
                            if fazerLogin(username, password, bdClientes):
                                userAutenticado = username
                                break
                        except clienteInexistenteError:
                            print("Utilizador não existe, volte a tentar")
                            break
                        print("0 - Voltar ao menu anterior")
                        password = input().strip()
                        if password == "0":
                            break
                    
            elif opcao == "3":
                # Guardar os dados ao sair do sistema
                guardarDados(bdClientes, bdContas, bdMovimento)
                print("\nA guardar os dados com segurança... Obrigado por usar o EISNT Bank!")
                break
            else:
                print("Opção inválida! Tente novamente.")
                
        else:
            # MENU DA CONTA (Autenticado)
            print(f"\n--- ÁREA DO CLIENTE ({userAutenticado}) ---")
            print("1. Consultar Saldo")
            print("2. Depositar Dinheiro")
            print("3. Levantar Dinheiro")
            print("4. Realizar Transferência")
            print("5. Consultar Extrato")
            print("6. Consultar Retorno")
            print("7. Gerar Relatório")
            print("8. Consultar Transferências")
            print("9. Terminar Sessão (Logout)")
            
            opcao = input("Escolha uma operação: ").strip()
            
            if opcao == "1":
                saldo = consultarSaldo(userAutenticado, bdContas)
                print(f"\nO seu saldo atual é de: {saldo:.2f}€")
                
            elif opcao == "2":
                print("\n[ DEPOSITAR SALDO ]")
                valor_texto = input("Introduza o valor a depositar (€): ").strip()
                while True:
                    try:
                        valor = float(valor_texto)
                    except ValueError:
                        print("Erro: Introduza um número válido para o valor.")
                        print("0 - Voltar ao menu anterior")
                        valor_texto = input().strip()
                        if valor_texto == "0":
                            break
                        continue
                    # 0 é um montante, não a opção de voltar.
                    if valor == 0:
                        print("Valor Incorrecto, insira o valor a depositar")
                        print("0 - Voltar ao menu anterior")
                        valor_texto = input().strip()
                        if valor_texto == "0":
                            break
                        continue
                    try:
                        depositarSaldo(userAutenticado, valor, bdContas, bdMovimento)
                        break
                    except ValorInvalidoError as e:
                        print(e)
                        print("0 - Voltar ao menu anterior")
                        valor_texto = input().strip()
                        if valor_texto == "0":
                            break

            elif opcao == "3":
                print("\n[ LEVANTAR SALDO ]")
                valor_texto = input("Introduza o valor a levantar (€): ").strip()
                while True:
                    try:
                        valor = float(valor_texto)
                    except ValueError:
                        print("Erro: Introduza um número válido para o valor.")
                        print("0 - Voltar ao menu anterior")
                        valor_texto = input().strip()
                        if valor_texto == "0":
                            break
                        continue
                    if valor == 0:
                        print("Valor Incorrecto, insira o valor a levantar")
                        print("0 - Voltar ao menu anterior")
                        valor_texto = input().strip()
                        if valor_texto == "0":
                            break
                        continue
                    try:
                        levantarSaldo(userAutenticado, valor, bdContas, bdMovimento)
                        break
                    except saldoInsuficienteError as e:
                        print(f"{str(e).rstrip('.')}, volte a tentar.")
                        print("0 - Voltar ao menu anterior")
                        valor_texto = input().strip()
                        if valor_texto == "0":
                            break
                    except ValorInvalidoError as e:
                        print(e)
                        print("0 - Voltar ao menu anterior")
                        valor_texto = input().strip()
                        if valor_texto == "0":
                            break

            elif opcao == "4":
                print("\n[ REALIZAR TRANSFERÊNCIA ]")
                destino = input("Username do destinatário: ").strip()
                voltar = False

                # O destinatário é verificado já aqui, antes de pedir o valor.
                while True:
                    if destino == userAutenticado:
                        print("O cliente de destino é o mesmo, por favor inserir novo destinatário para a transferência")
                        print("0 - Voltar ao menu anterior / Cancelar")
                        destino = input().strip()
                        if destino == "0":
                            voltar = True
                            break
                        continue
                    try:
                        if destino not in bdContas:
                            raise clienteInexistenteError(destino)
                    except clienteInexistenteError:
                        print("Utilizador não existe, volte a tentar")
                        print("0 - Voltar ao menu anterior")
                        destino = input().strip()
                        if destino == "0":
                            voltar = True
                            break
                        continue
                    break

                if not voltar:
                    valor_texto = input("Valor a transferir (€): ").strip()
                    while True:
                        try:
                            valor = float(valor_texto)
                        except ValueError:
                            print("Erro: Introduza um número válido para o valor.")
                            print("0 - Voltar ao menu anterior")
                            valor_texto = input().strip()
                            if valor_texto == "0":
                                break
                            continue
                        # 0 é um montante, não a opção de voltar.
                        if valor == 0:
                            print("Valor Incorrecto, insira o valor a transferir")
                            print("0 - Voltar ao menu anterior")
                            valor_texto = input().strip()
                            if valor_texto == "0":
                                break
                            continue
                        try:
                            transferirValor(userAutenticado, destino, valor, bdContas, bdMovimento)
                            break
                        except clienteInexistenteError:
                            print("Utilizador não existe, volte a tentar")
                            break
                        except saldoInsuficienteError as e:
                            print(f"{str(e).rstrip('.')}, volte a tentar.")
                            print("0 - Voltar ao menu anterior")
                            valor_texto = input().strip()
                            if valor_texto == "0":
                                break
                        except ValorInvalidoError as e:
                            print(e)
                            print("0 - Voltar ao menu anterior")
                            valor_texto = input().strip()
                            if valor_texto == "0":
                                break
                    
            elif opcao == "5":
                print("\n[ EXTRATO DA CONTA ]")
                movimentos = consultarMovimentos(userAutenticado, bdMovimento)
                if not movimentos:
                    print("Ainda não existem movimentos nesta conta.")
                else:
                    print(f"{'Data':<20} {'Tipo':<16} {'Valor':>10}  {'Origem':<16} {'Destino':<16}")
                    print("-" * 80)
                    for t in movimentos:
                        print(
                            f"{t.data_hora:<20} {t.tipo:<16} {t.valor:>10.2f}€ "
                            f"{t.userOrigem:<16} {t.userDestino:<16}"
                        )
                    
            elif opcao == "6":
                print("\n[ CONSULTAR RETORNO ]")
                saldo_atual = consultarSaldo(userAutenticado, bdContas)
                consultarRetorno(saldo_atual)

            elif opcao == "7":
                print("\n[ GERAR RELATÓRIO ]")
                # Um processo lê os saldos e o outro conta as transferências.
                fila_saldos = multiprocessing.Queue()
                fila_transferencias = multiprocessing.Queue()
                processo_saldos = multiprocessing.Process(
                    target=recolherSaldos, args=(bdContas, fila_saldos)
                )
                processo_transferencias = multiprocessing.Process(
                    target=recolherNumeroTransferencias,
                    args=(bdMovimento, fila_transferencias),
                )
                processo_saldos.start()
                processo_transferencias.start()
                saldos = fila_saldos.get()
                totais = fila_transferencias.get()
                processo_saldos.join()
                processo_transferencias.join()

                linhas = []
                for username, saldo in saldos.items():
                    linhas.append({
                        "username": username,
                        "transferencias": totais.get(username, 0),
                        "saldo": saldo,
                    })
                mostrarRelatorioSistema(ordenarLinhasPorSaldo(linhas))

            elif opcao == "8":
                print("\n[ CONSULTAR TRANSFERÊNCIAS ]")
                consultarTransferencias(userAutenticado, bdMovimento)

            elif opcao == "9":
                print(f"\nSessão terminada para {userAutenticado}.")
                userAutenticado = None
                limpar_ecra()
            else:
                print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    main()
