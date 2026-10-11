"""Fixtures compartilhadas entre os testes.

A fixture `repo` é parametrizada: ela roda cada teste DUAS vezes,
uma para cada backend (json e sqlite). Assim, a mesma suíte valida
os dois repositórios sem duplicar código.
"""
import pytest

from financas.repositories import (
    JsonTransacaoRepository,
    SqliteTransacaoRepository,
)

BACKENDS = ["json", "sqlite"]


@pytest.fixture(params=BACKENDS)
def repo(request, tmp_path):
    """Cria um repositório isolado no backend atual do teste.

    - request.param: 'json' ou 'sqlite' (o pytest injeta automaticamente)
    - tmp_path: pasta temporária única por teste (também do pytest)
    """
    backend = request.param

    if backend == "json":
        return JsonTransacaoRepository(tmp_path / "transacoes.json")

    if backend == "sqlite":
        return SqliteTransacaoRepository(tmp_path / "financas.db")

    raise ValueError(f"Backend desconhecido: {backend}")