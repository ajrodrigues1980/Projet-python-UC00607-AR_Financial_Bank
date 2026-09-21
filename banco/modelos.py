from dataclasses import dataclass
from datetime import datetime

"""Criação das classes Cliente e Conta e Transação usando dataclasses
# para simplificar a definição de classes com atributos."""
@dataclass
class Cliente:
    username: str
    password: str
    
@dataclass
class Conta:
    username: str
    saldo: float = 0.0

@dataclass
class Transacao:
    userOrigem: str
    userDestino: str
    tipo: str  # "depósito" ou "levantamento"
    valor: float
    data_hora: str
