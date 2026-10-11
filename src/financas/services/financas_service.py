from typing import Dict, List

from financas.models import TipoTransacao, Transacao
from financas.repositories import JsonTransacaoRepository


class FinancasService:
    """Regras de negócio de finanças pessoais.

    Não conhece JSON, SQLite, CLI ou GUI. Só sabe calcular e orquestrar
    operações sobre transações usando um repositório injetado.
    """

    def __init__(self, repositorio: JsonTransacaoRepository):
        self.repo = repositorio

    # ---------- Cadastro ----------
    def adicionar(self, transacao: Transacao) -> None:
        """Adiciona uma transação."""
        self.repo.adicionar(transacao)

    def remover(self, transacao_id: str) -> bool:
        """Remove uma transação pelo ID. Retorna True se removeu."""
        return self.repo.remover(transacao_id)

    def listar(self) -> List[Transacao]:
        """Lista todas as transações."""
        return self.repo.listar()

    # ---------- Cálculos ----------
    def total_receitas(self) -> float:
        """Soma de todas as receitas."""
        return sum(t.valor for t in self.listar() if t.tipo == TipoTransacao.RECEITA)

    def total_despesas(self) -> float:
        """Soma de todas as despesas."""
        return sum(t.valor for t in self.listar() if t.tipo == TipoTransacao.DESPESA)

    def saldo(self) -> float:
        """Saldo atual: receitas - despesas."""
        return self.total_receitas() - self.total_despesas()

    def por_categoria(self) -> Dict[str, Dict[str, float]]:
        """Agrupa totais por categoria.

        Retorna:
            {
                "Alimentacao": {"receita": 0.0, "despesa": 150.0, "saldo": -150.0},
                "Trabalho":    {"receita": 5000.0, "despesa": 0.0, "saldo": 5000.0},
            }
        """
        resultado: Dict[str, Dict[str, float]] = {}
        for t in self.listar():
            bucket = resultado.setdefault(
                t.categoria, {"receita": 0.0, "despesa": 0.0, "saldo": 0.0}
            )
            bucket[t.tipo.value] += t.valor
            bucket["saldo"] = bucket["receita"] - bucket["despesa"]
        return resultado