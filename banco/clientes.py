""" Módulo de Gestão de Clientes - Faz o registo de novos clientes, 
validação de segurança e a autenticação de clientes existentes"""

from banco.modelos import Cliente, Conta
from banco.excecoes import clienteJaExisteError, clienteInexistenteError

def criarCliente(username: str, password: str, bdClientes: dict, bdContas: dict) -> bool:
    
    # Verifica a existência do username no sistema
    if username in bdClientes:
        raise clienteJaExisteError(username)
    
    # Valida o tamanho da password (entre 6 e 10 caracteres)
    if not (6 <= len(password) <= 10):
        print("Erro: A password deve conter entre 6 a 10 caracteres.")
        return False

    # Valida se a password tem pelo menos 1 letra e 1 número
    if not any(char.isalpha() for char in password) or not any(char.isdigit() for char in password):
        print("Erro: A password deve conter pelo menos 1 letra e 1 número.")
        return False
    
    """ No caso de Validação correcta, Cria o cliente e a conta associada no sistema, 
     adicionando-os aos dicionários bdClientes e bdContas"""
    bdClientes[username] = Cliente(username=username, password=password)
    bdContas[username] = Conta(username=username, saldo=0.00)
    
    print(f"Sucesso: O cliente '{username}' foi criado com sucesso!")
    return True

# Função para verificar a existência de um cliente e caso exista, autenticá-lo no sistema
def fazerLogin(username: str, password: str, bdClientes: dict) -> bool:
    
    # Verificação da existencia cliente
    if username not in bdClientes:
        raise clienteInexistenteError(username)
        
    # Verifica se a password digitada coincide
    cliente = bdClientes[username]
    if cliente.password != password:
        print("Erro: Palavra-passe incorreta.")
        return False
        
    print(f"Bem-vindo , {username}!")
    return True