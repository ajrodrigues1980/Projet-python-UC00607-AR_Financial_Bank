# Programa Principal do Sistema Bancário - EISNT Bank 
import os
# Titulo Bonito com pyfiglet :)
try:
    import pyfiglet
    TEM_FIGLET = True
except ImportError:
    TEM_FIGLET = False

# Importação dos módulos
from banco.modelos import Cliente, Conta, Transacao
from banco.clientes import criarCliente, fazerLogin
from banco.contas import consultarSaldo, depositarSaldo, transferirValor
from banco.guardarDados import carregarDados, guardarDados
from banco.excecoes import clienteJaExisteError, clienteInexistenteError, saldoInsuficienteError

# Inicializar as "Bases de Dados" na memória RAM
bdClientes = {}
bdContas = {}
bdMovimento = []

def limpar_ecra():
    
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
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
                password = input("Password (6-10 chars, 1 letra, 1 número): ").strip()
                
                try:
                    criarCliente(username, password, bdClientes, bdContas)
                except clienteJaExisteError as e:
                    print(e)  # Imprime mensagem de erro personalizada
                    
            elif opcao == "2":
                print("\n[ ENTRAR NO SISTEMA ]")
                username = input("Username: ").strip()
                password = input("Password: ").strip()
                
                try:
                    if fazerLogin(username, password, bdClientes):
                        userAutenticado = username
                except clienteInexistenteError as e:
                    print(e)
                    
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
            print("3. Realizar Transferência")
            print("4. Terminar Sessão (Logout)")
            
            opcao = input("Escolha uma operação: ").strip()
            
            if opcao == "1":
                saldo = consultarSaldo(userAutenticado, bdContas)
                print(f"\nO seu saldo atual é de: {saldo:.2f}€")
                
            elif opcao == "2":
                print("\n[ DEPOSITAR SALDO ]")
                try:
                    valor = float(input("Introduza o valor a depositar (€): "))
                    depositarSaldo(userAutenticado, valor, bdContas)
                except ValueError:
                    print("Erro: Introduza um número válido para o valor.")
                    
            elif opcao == "3":
                print("\n[ REALIZAR TRANSFERÊNCIA ]")
                destino = input("Username do destinatário: ").strip()
                try:
                    valor = float(input("Valor a transferir (€): "))
                    transferirValor(userAutenticado, destino, valor, bdContas, bdMovimento)
                except clienteInexistenteError as e:
                    print(e)
                except saldoInsuficienteError as e:
                    print(e)
                except ValueError:
                    print("Erro: Introduza um número válido para o valor.")
                    
            elif opcao == "4":
                print(f"\nSessão terminada para {userAutenticado}.")
                userAutenticado = None
                limpar_ecra()

if __name__ == "__main__":
    main()
