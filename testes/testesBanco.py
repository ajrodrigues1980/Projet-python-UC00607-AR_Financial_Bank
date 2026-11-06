"""Testes das regras pedidas no guião: criação duplicada e transferências."""

import pytest

from banco.clientes import criarCliente
from banco.contas import depositarSaldo, transferirValor
from banco.excecoes import (
    clienteJaExisteError,
    clienteInexistenteError,
    saldoInsuficienteError,
)
from banco.modelos import Cliente, Conta


def test_criar_cliente_username_existente():
    """Criar um username que já existe lança clienteJaExisteError."""
    bd_clientes = {"ana": Cliente(username="ana", password="ana123")}
    bd_contas = {"ana": Conta(username="ana", saldo=0.0)}

    with pytest.raises(clienteJaExisteError):
        criarCliente("ana", "outr4s", bd_clientes, bd_contas)


def test_transferencia_utilizador_inexistente():
    """Transferir para um username que não existe lança clienteInexistenteError."""
    bd_contas = {"ana": Conta(username="ana", saldo=100.0)}

    with pytest.raises(clienteInexistenteError):
        transferirValor("ana", "inexistente", 10.0, bd_contas, [])


def test_deposito_com_sucesso():
    """Um depósito válido aumenta o saldo e regista o movimento."""
    bd_contas = {"ana": Conta(username="ana", saldo=10.0)}
    movimentos = []

    resultado = depositarSaldo("ana", 25.0, bd_contas, movimentos)

    assert resultado is True
    assert bd_contas["ana"].saldo == 35.0
    assert len(movimentos) == 1
    assert movimentos[0].tipo == "Depósito"
    assert movimentos[0].valor == 25.0


def test_transferencia_com_sucesso():
    """Uma transferência válida move o saldo e regista o movimento."""
    bd_contas = {
        "ana": Conta(username="ana", saldo=100.0),
        "bob": Conta(username="bob", saldo=20.0),
    }
    movimentos = []

    resultado = transferirValor("ana", "bob", 30.0, bd_contas, movimentos)

    assert resultado is True
    assert bd_contas["ana"].saldo == 70.0
    assert bd_contas["bob"].saldo == 50.0
    assert len(movimentos) == 1
    assert movimentos[0].valor == 30.0
    assert movimentos[0].tipo == "Transferência"


def test_transferencia_saldo_insuficiente():
    """Pedir mais do que o saldo lança saldoInsuficienteError e não altera as contas."""
    bd_contas = {
        "ana": Conta(username="ana", saldo=100.0),
        "bob": Conta(username="bob", saldo=20.0),
    }
    movimentos = []

    with pytest.raises(saldoInsuficienteError):
        transferirValor("ana", "bob", 150.0, bd_contas, movimentos)

    # A transferência falhou, por isso os saldos e o histórico ficam como estavam.
    assert bd_contas["ana"].saldo == 100.0
    assert bd_contas["bob"].saldo == 20.0
    assert movimentos == []
