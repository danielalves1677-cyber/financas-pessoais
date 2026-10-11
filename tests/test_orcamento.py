"""Testes de orçamentos — parametrizados nos dois backends."""
import pytest

from financas.models import Orcamento, Transacao, TipoTransacao
from financas.services import FinancasService


@pytest.fixture
def service(repo):
    return FinancasService(repo)


def test_sem_orcamentos(service):
    assert service.listar_orcamentos() == []
    assert service.status_orcamento() == []


def test_salvar_e_listar_orcamento(service):
    service.salvar_orcamento(Orcamento(categoria="Alimentacao", limite_mensal=500))
    orcs = service.listar_orcamentos()
    assert len(orcs) == 1
    assert orcs[0].categoria == "Alimentacao"
    assert orcs[0].limite_mensal == 500


def test_upsert_orcamento(service):
    """Salvar duas vezes a mesma categoria deve atualizar, não duplicar."""
    service.salvar_orcamento(Orcamento(categoria="Alimentacao", limite_mensal=500))
    service.salvar_orcamento(Orcamento(categoria="Alimentacao", limite_mensal=800))
    orcs = service.listar_orcamentos()
    assert len(orcs) == 1
    assert orcs[0].limite_mensal == 800


def test_remover_orcamento(service):
    orc = Orcamento(categoria="Alimentacao", limite_mensal=500)
    service.salvar_orcamento(orc)
    orcs = service.listar_orcamentos()
    assert service.remover_orcamento(orcs[0].id) is True
    assert service.listar_orcamentos() == []


def test_remover_orcamento_inexistente(service):
    assert service.remover_orcamento("id-que-nao-existe") is False


def test_status_ok(service):
    """Gasto abaixo de 80% do limite → status 'ok'."""
    service.salvar_orcamento(Orcamento(categoria="Alimentacao", limite_mensal=1000))
    service.adicionar(
        Transacao(
            descricao="Mercado",
            valor=500,
            tipo=TipoTransacao.DESPESA,
            categoria="Alimentacao",
        )
    )
    status = service.status_orcamento()
    assert len(status) == 1
    assert status[0]["status"] == "ok"
    assert status[0]["gasto"] == 500
    assert status[0]["percentual"] == 50.0


def test_status_alerta(service):
    """Gasto entre 80% e 100% → status 'alerta'."""
    service.salvar_orcamento(Orcamento(categoria="Alimentacao", limite_mensal=1000))
    service.adicionar(
        Transacao(
            descricao="Mercado",
            valor=850,
            tipo=TipoTransacao.DESPESA,
            categoria="Alimentacao",
        )
    )
    status = service.status_orcamento()
    assert status[0]["status"] == "alerta"
    assert status[0]["percentual"] == 85.0


def test_status_estourado(service):
    """Gasto acima de 100% → status 'estourado'."""
    service.salvar_orcamento(Orcamento(categoria="Alimentacao", limite_mensal=1000))
    service.adicionar(
        Transacao(
            descricao="Mercado",
            valor=1200,
            tipo=TipoTransacao.DESPESA,
            categoria="Alimentacao",
        )
    )
    status = service.status_orcamento()
    assert status[0]["status"] == "estourado"
    assert status[0]["percentual"] == 120.0


def test_receitas_nao_contam_no_orcamento(service):
    """Só despesas contam no gasto do orçamento."""
    service.salvar_orcamento(Orcamento(categoria="Alimentacao", limite_mensal=1000))
    service.adicionar(
        Transacao(
            descricao="Reembolso",
            valor=500,
            tipo=TipoTransacao.RECEITA,
            categoria="Alimentacao",
        )
    )
    status = service.status_orcamento()
    assert status[0]["gasto"] == 0
    assert status[0]["status"] == "ok"


def test_orcamento_case_insensitive(service):
    """Categoria 'alimentacao' deve bater com orçamento 'Alimentacao'."""
    service.salvar_orcamento(Orcamento(categoria="Alimentacao", limite_mensal=1000))
    service.adicionar(
        Transacao(
            descricao="Mercado",
            valor=900,
            tipo=TipoTransacao.DESPESA,
            categoria="alimentacao",
        )
    )
    status = service.status_orcamento()
    assert status[0]["gasto"] == 900
    assert status[0]["status"] == "alerta"