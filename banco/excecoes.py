# Módulo de excepções técnicas para o Sistema Bancário

# Erro ao criar um cliente novo e já existe o username indicado na base de dados
class clienteJaExisteError(Exception): 
    
    def __init__(self, username):
        self.message = f"Erro: O cliente com o username '{username}' já se encontra registado no sistema!"
        super().__init__(self.message)
        
# Erro de cliente inexistente no login e/ou no destino de uma transferência
class clienteInexistenteError(Exception):
    
    def __init__(self, username: str):
        self.message = f"Erro: O Cliente com o username '{username}' não foi encontrado no sistema."
        super().__init__(self.message)
        
# Erro quando se tenta levantar ou transferir um valor maior que o saldo disponível
class saldoInsuficienteError(Exception):
    
    def __init__(self, saldo_atual: float, valor_pedido: float):
        self.message = f"Erro: O seu Saldo é insuficiente. Saldo atual: {saldo_atual:.2f}€ | Valor pedido: {valor_pedido:.2f}€."
        super().__init__(self.message)