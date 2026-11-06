"""Estruturas do sistema: utilizador, conta e transação."""

from dataclasses import dataclass


@dataclass
class Cliente:
    """Utilizador do sistema: username único e password."""
    username: str
    password: str


@dataclass
class Conta:
    """Conta associada a um utilizador, com o saldo atual."""
    username: str
    saldo: float = 0.0


@dataclass
class Transacao:
    """Movimento entre contas, ou da própria conta no depósito e no levantamento."""
    userOrigem: str
    userDestino: str
    tipo: str
    valor: float
    data_hora: str
