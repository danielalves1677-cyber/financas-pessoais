"""Testes do repositório — rodam nos backends JSON e SQLite.

A fixture `repo` está definida em tests/conftest.py e é parametrizada:
cada teste abaixo roda 2x (uma por backend).
"""
import pytest

from financas.models import Transacao, TipoTransacao


def test_repo_comeca_vazio(repo):
    assert repo.listar() == []


def test_adicionar_e_listar(repo):
    t = Transacao(
        descricao="Uber",
        valor=25,
        tipo=TipoTransacao.DESPESA,
        categoria="Transporte",
    )
    repo.adicionar(t)
    resultado = repo.listar()
    assert len(resultado) == 1
    assert resultado[0].descricao == "Uber"
    assert resultado[0].valor == 25


def test_remover_existente(repo):
    t = Transacao(
        descricao="X",
        valor=10,
        tipo=TipoTransacao.DESPESA,
        categoria="Y",
    )
    repo.adicionar(t)
    assert repo.remover(t.id) is True
    assert repo.listar() == []


def test_remover_inexistente(repo):
    assert repo.remover("id-que-nao-existe") is False


def test_persistencia_entre_instancias(tmp_path):
    """Teste específico de persistência: cria dois repositórios do MESMO
    tipo apontando para o MESMO arquivo, e valida que os dados sobrevivem.
    """
    # Testa apenas com JSON aqui (SQLite é mais pesado pra criar/instanciar)
    from financas.repositories import JsonTransacaoRepository

    caminho = tmp_path / "compartilhado.json"

    repo1 = JsonTransacaoRepository(caminho)
    repo1.adicionar(
        Transacao(
            descricao="Salario",
            valor=1000,
            tipo=TipoTransacao.RECEITA,
            categoria="Trabalho",
        )
    )

    repo2 = JsonTransacaoRepository(caminho)
    assert len(repo2.listar()) == 1
    assert repo2.listar()[0].descricao == "Salario"