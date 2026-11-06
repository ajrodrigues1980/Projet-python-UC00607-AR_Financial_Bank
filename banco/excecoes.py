"""Excepções do sistema bancário.

Os três primeiros nomes são opção pessoal, combinada com o professor.
PasswordInvalidaError e ValorInvalidoError são extras.
"""


class clienteJaExisteError(Exception):
    """Lançada quando o username indicado já está registado."""
    def __init__(self, username):
        self.message = (
            f"Erro: O cliente com o username '{username}' já se encontra registado no sistema!"
        )
        super().__init__(self.message)


class clienteInexistenteError(Exception):
    """Lançada no login ou quando o destino de uma transferência não existe."""
    def __init__(self, username: str):
        self.message = (
            f"Erro: O Cliente com o username '{username}' não foi encontrado no sistema."
        )
        super().__init__(self.message)


class saldoInsuficienteError(Exception):
    """Lançada quando o levantamento ou a transferência pedem mais do que o saldo."""
    def __init__(self, saldo_atual: float, valor_pedido: float):
        self.message = (
            f"Erro: O seu Saldo é insuficiente. "
            f"Saldo atual: {saldo_atual:.2f}€ | Valor pedido: {valor_pedido:.2f}€."
        )
        super().__init__(self.message)


class PasswordInvalidaError(Exception):
    """Lançada quando a password não tem 6 a 10 caracteres, com letra e número."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ValorInvalidoError(Exception):
    """Lançada quando o valor do movimento não é maior que zero, ou o destino é a própria conta."""
    def __init__(self, message: str = "Erro: O valor deve ser maior que zero."):
        self.message = message
        super().__init__(self.message)
