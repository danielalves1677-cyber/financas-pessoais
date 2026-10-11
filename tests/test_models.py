import pytest
from pydantic import ValidationError

from financas.models import Transacao, TipoTransacao


def test_criar_transacao_valida():
    t = Transacao(
        descricao="Salario",
        valor=5000,
        tipo=TipoTransacao.RECEITA,
        categoria="Trabalho",
    )
    assert t.valor == 5000
    assert t.tipo == TipoTransacao.RECEITA
    assert t.id  # UUID gerado automaticamente
    assert t.data  # Data gerada automaticamente


def test_valor_negativo_falha():
    with pytest.raises(ValidationError):
        Transacao(
            descricao="X",
            valor=-10,
            tipo=TipoTransacao.DESPESA,
            categoria="Y",
        )


def test_valor_zero_falha():
    with pytest.raises(ValidationError):
        Transacao(
            descricao="X",
            valor=0,
            tipo=TipoTransacao.DESPESA,
            categoria="Y",
        )


def test_descricao_vazia_falha():
    with pytest.raises(ValidationError):
        Transacao(
            descricao="   ",
            valor=10,
            tipo=TipoTransacao.DESPESA,
            categoria="Y",
        )


def test_serializacao_roundtrip():
    """to_dict() seguido de from_dict() deve devolver a mesma transação."""
    original = Transacao(
        descricao="Cafe",
        valor=5.5,
        tipo=TipoTransacao.DESPESA,
        categoria="Alimentacao",
    )
    reconstruida = Transacao.from_dict(original.to_dict())
    assert original.id == reconstruida.id
    assert original.descricao == reconstruida.descricao
    assert original.valor == reconstruida.valor
    assert original.tipo == reconstruida.tipo
    assert original.categoria == reconstruida.categoria