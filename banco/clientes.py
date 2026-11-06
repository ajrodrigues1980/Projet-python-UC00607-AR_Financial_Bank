""" Módulo de Gestão de Clientes - Faz o registo de novos clientes, 
validação de segurança e a autenticação de clientes existentes"""

from banco.modelos import Cliente, Conta
from banco.excecoes import (
    clienteJaExisteError,
    clienteInexistenteError,
    PasswordInvalidaError,
)

def criarCliente(username: str, password: str, bd_clientes: dict, bd_contas: dict) -> bool:
    """Regista um cliente novo e a conta associada, com saldo zero.

    Args:
        username: nome único do cliente.
        password: password com 6 a 10 caracteres, pelo menos uma letra e um número.
        bd_clientes: clientes existentes, indexados por username.
        bd_contas: contas existentes, indexadas por username.

    Returns:
        True quando o cliente e a conta ficam registados.

    Raises:
        clienteJaExisteError: o username já está registado.
        PasswordInvalidaError: a password não cumpre as regras.
    """
    # O username é a chave do dicionário, por isso um repetido substituiria o cliente.
    if username in bd_clientes:
        raise clienteJaExisteError(username)

    # As duas regras separam mensagens diferentes: tamanho, e letra com número.
    if not (6 <= len(password) <= 10):
        raise PasswordInvalidaError("Erro: A password deve conter entre 6 a 10 caracteres.")

    if not any(char.isalpha() for char in password) or not any(char.isdigit() for char in password):
        raise PasswordInvalidaError("Erro: A password deve conter pelo menos 1 letra e 1 número.")

    bd_clientes[username] = Cliente(username=username, password=password)
    bd_contas[username] = Conta(username=username, saldo=0.00)

    print(f"Sucesso: O cliente '{username}' foi criado com sucesso!")
    return True


def fazerLogin(username: str, password: str, bd_clientes: dict) -> bool:
    """Confirma se o username existe e se a password coincide.

    Args:
        username: nome do cliente que quer entrar.
        password: password introduzida.
        bd_clientes: clientes existentes, indexados por username.

    Returns:
        True se a password coincide. False se a password está errada.

    Raises:
        clienteInexistenteError: não existe cliente com esse username.
    """
    if username not in bd_clientes:
        raise clienteInexistenteError(username)

    # A password errada não é excepção: o cliente existe, a tentativa é que falhou.
    cliente = bd_clientes[username]
    if cliente.password != password:
        print("Erro: Palavra-passe incorreta.")
        return False

    print(f"Bem-vindo , {username}!")
    return True