from datetime import datetime
from typing import Dict, List

from financas.models import Orcamento, TipoTransacao, Transacao
from financas.repositories import JsonTransacaoRepository, SqliteTransacaoRepository


class FinancasService:
    """Regras de negócio de finanças pessoais."""

    def __init__(self, repositorio):
        self.repo = repositorio

    # ---------- Cadastro de transações ----------
    def adicionar(self, transacao: Transacao) -> None:
        self.repo.adicionar(transacao)

    def remover(self, transacao_id: str) -> bool:
        return self.repo.remover(transacao_id)

    def listar(self) -> List[Transacao]:
        return self.repo.listar()

    # ---------- Cadastro de orçamentos ----------
    def salvar_orcamento(self, orcamento: Orcamento) -> None:
        self.repo.salvar_orcamento(orcamento)

    def remover_orcamento(self, orcamento_id: str) -> bool:
        return self.repo.remover_orcamento(orcamento_id)

    def listar_orcamentos(self) -> List[Orcamento]:
        return self.repo.listar_orcamentos()

    # ---------- Cálculos gerais ----------
    def total_receitas(self) -> float:
        return sum(t.valor for t in self.listar() if t.tipo == TipoTransacao.RECEITA)

    def total_despesas(self) -> float:
        return sum(t.valor for t in self.listar() if t.tipo == TipoTransacao.DESPESA)

    def saldo(self) -> float:
        return self.total_receitas() - self.total_despesas()

    def por_categoria(self) -> Dict[str, Dict[str, float]]:
        resultado: Dict[str, Dict[str, float]] = {}
        for t in self.listar():
            bucket = resultado.setdefault(
                t.categoria, {"receita": 0.0, "despesa": 0.0, "saldo": 0.0}
            )
            bucket[t.tipo.value] += t.valor
            bucket["saldo"] = bucket["receita"] - bucket["despesa"]
        return resultado

    # ---------- Regras de orçamento ----------
    def gasto_mes_atual(self, categoria: str) -> float:
        """Soma das despesas da categoria no mês atual."""
        agora = datetime.now()
        total = 0.0
        for t in self.listar():
            if (
                t.tipo == TipoTransacao.DESPESA
                and t.categoria.lower() == categoria.lower()
                and t.data.year == agora.year
                and t.data.month == agora.month
            ):
                total += t.valor
        return total

    def status_orcamento(self) -> List[Dict]:
        """Retorna o status de cada orçamento no mês atual.

        Cada item contém:
            - categoria
            - limite
            - gasto
            - percentual (0-∞)
            - status: 'ok' | 'alerta' | 'estourado'
        """
        resultado = []
        for orc in self.listar_orcamentos():
            gasto = self.gasto_mes_atual(orc.categoria)
            percentual = (gasto / orc.limite_mensal) * 100 if orc.limite_mensal else 0

            if gasto > orc.limite_mensal:
                status = "estourado"
            elif percentual >= 80:
                status = "alerta"
            else:
                status = "ok"

            resultado.append(
                {
                    "orcamento": orc,
                    "categoria": orc.categoria,
                    "limite": orc.limite_mensal,
                    "gasto": gasto,
                    "percentual": percentual,
                    "status": status,
                }
            )
        return resultado