"""Testes de metas financeiras — parametrizados nos dois backends."""
from datetime import date, timedelta

import pytest

from financas.models import Meta
from financas.services import FinancasService


@pytest.fixture
def service(repo):
    return FinancasService(repo)


def _meta_exemplo(prazo_dias: int = 180) -> Meta:
    return Meta(
        nome="Viagem",
        valor_alvo=10000,
        valor_atual=0,
        prazo=date.today() + timedelta(days=prazo_dias),
    )


def test_sem_metas(service):
    assert service.listar_metas() == []
    assert service.status_metas() == []


def test_criar_e_listar_meta(service):
    meta = _meta_exemplo()
    service.salvar_meta(meta)
    metas = service.listar_metas()
    assert len(metas) == 1
    assert metas[0].nome == "Viagem"
    assert metas[0].valor_alvo == 10000


def test_upsert_meta(service):
    meta = _meta_exemplo()
    service.salvar_meta(meta)
    meta.valor_atual = 5000
    service.salvar_meta(meta)
    metas = service.listar_metas()
    assert len(metas) == 1
    assert metas[0].valor_atual == 5000


def test_remover_meta(service):
    meta = _meta_exemplo()
    service.salvar_meta(meta)
    assert service.remover_meta(meta.id) is True
    assert service.listar_metas() == []


def test_remover_meta_inexistente(service):
    assert service.remover_meta("id-que-nao-existe") is False


def test_progresso_meta(service):
    meta = _meta_exemplo()
    meta.valor_atual = 2500
    assert service.progresso_meta(meta) == 25.0


def test_valor_mensal_necessario(service):
    """Prazo ~180 dias = 6 meses. Falta 10000 → 1666.67/mês."""
    meta = _meta_exemplo(prazo_dias=180)
    mensal = service.valor_mensal_necessario(meta)
    assert mensal == pytest.approx(10000 / 6, rel=0.05)


def test_status_em_dia(service):
    meta = _meta_exemplo()
    service.salvar_meta(meta)
    status = service.status_metas()
    assert status[0]["status"] == "em_dia"


def test_status_concluida(service):
    meta = _meta_exemplo()
    meta.valor_atual = 10000
    service.salvar_meta(meta)
    status = service.status_metas()
    assert status[0]["status"] == "concluida"
    assert status[0]["progresso"] == 100.0


def test_status_atrasada(service):
    meta = Meta(
        nome="Antiga",
        valor_alvo=1000,
        valor_atual=500,
        prazo=date.today() - timedelta(days=10),
    )
    service.salvar_meta(meta)
    status = service.status_metas()
    assert status[0]["status"] == "atrasada"
    assert status[0]["dias_restantes"] < 0


def test_meta_ja_concluida_nao_precisa_guardar(service):
    meta = _meta_exemplo()
    meta.valor_atual = 12000
    assert service.valor_mensal_necessario(meta) == 0.0


def test_dias_restantes(service):
    meta = _meta_exemplo(prazo_dias=30)
    dias = service.dias_restantes(meta)
    assert dias == 30