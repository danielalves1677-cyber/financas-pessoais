"""Testes do serviço — também rodam nos dois backends."""
import pytest

from financas.models import Transacao, TipoTransacao
from financas.services import FinancasService


@pytest.fixture
def service(repo):
    """Envolve o repositório num FinancasService."""
    return FinancasService(repo)


def test_saldo_inicial_zero(service):
    assert service.total_receitas() == 0
    assert service.total_despesas() == 0
    assert service.saldo() == 0


def test_calculo_de_saldo(service):
    service.adicionar(
        Transacao(
            descricao="Salario",
            valor=5000,
            tipo=TipoTransacao.RECEITA,
            categoria="Trabalho",
        )
    )
    service.adicionar(
        Transacao(
            descricao="Mercado",
            valor=300,
            tipo=TipoTransacao.DESPESA,
            categoria="Alimentacao",
        )
    )
    assert service.total_receitas() == 5000
    assert service.total_despesas() == 300
    assert service.saldo() == 4700


def test_por_categoria(service):
    service.adicionar(
        Transacao(
            descricao="Almoco",
            valor=30,
            tipo=TipoTransacao.DESPESA,
            categoria="Alimentacao",
        )
    )
    service.adicionar(
        Transacao(
            descricao="Jantar",
            valor=40,
            tipo=TipoTransacao.DESPESA,
            categoria="Alimentacao",
        )
    )
    service.adicionar(
        Transacao(
            descricao="Salario",
            valor=1000,
            tipo=TipoTransacao.RECEITA,
            categoria="Trabalho",
        )
    )

    dados = service.por_categoria()
    assert dados["Alimentacao"]["despesa"] == 70
    assert dados["Alimentacao"]["receita"] == 0
    assert dados["Alimentacao"]["saldo"] == -70
    assert dados["Trabalho"]["receita"] == 1000
    assert dados["Trabalho"]["saldo"] == 1000


def test_remover_via_service(service):
    t = Transacao(
        descricao="Cafe",
        valor=5,
        tipo=TipoTransacao.DESPESA,
        categoria="Alimentacao",
    )
    service.adicionar(t)
    assert len(service.listar()) == 1
    assert service.remover(t.id) is True
    assert len(service.listar()) == 0