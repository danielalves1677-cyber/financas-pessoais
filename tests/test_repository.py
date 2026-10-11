import pytest

from financas.models import Transacao, TipoTransacao
from financas.repositories import JsonTransacaoRepository


@pytest.fixture
def repo(tmp_path):
    """Cria um repositório usando um arquivo temporário isolado por teste."""
    return JsonTransacaoRepository(tmp_path / "transacoes.json")


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
    """Dados gravados numa instância devem aparecer em outra no mesmo arquivo."""
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