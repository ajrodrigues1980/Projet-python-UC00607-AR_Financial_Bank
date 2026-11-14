"""Ligação ao Firebase Firestore (Parte 1 UC00610).

A ligação é feita uma só vez quando este módulo é importado.
A chave fica na raiz do projeto: chave.json (ignorada pelo Git).
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore

# Raiz do projeto = pasta acima de banco/
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHEIRO_CHAVE = os.path.join(_RAIZ, "chave.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(FICHEIRO_CHAVE)
    firebase_admin.initialize_app(cred)

db = firestore.client()


def testar_ligacao():
    """Escreve um documento de teste na coleção teste (prova da Parte 1)."""
    db.collection("teste").document("ligacao").set({
        "mensagem": "Olá Firestore — EISNT Bank",
        "data": firestore.SERVER_TIMESTAMP,
    })