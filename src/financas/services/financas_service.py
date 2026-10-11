from datetime import datetime
from typing import Dict, List

from financas.models import Meta, Orcamento, TipoTransacao, Transacao


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

    # ---------- Cadastro de metas ----------
    def salvar_meta(self, meta: Meta) -> None:
        self.repo.salvar_meta(meta)

    def remover_meta(self, meta_id: str) -> bool:
        return self.repo.remover_meta(meta_id)

    def listar_metas(self) -> List[Meta]:
        return self.repo.listar_metas()

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

    # ---------- Regras de meta ----------
    @staticmethod
    def progresso_meta(meta: Meta) -> float:
        if meta.valor_alvo <= 0:
            return 0.0
        return (meta.valor_atual / meta.valor_alvo) * 100

    @staticmethod
    def dias_restantes(meta: Meta) -> int:
        return (meta.prazo - datetime.now().date()).days

    @staticmethod
    def meses_restantes(meta: Meta) -> int:
        dias = (meta.prazo - datetime.now().date()).days
        if dias <= 0:
            return 0
        return max(1, (dias + 29) // 30)

    @staticmethod
    def valor_mensal_necessario(meta: Meta) -> float:
        falta = meta.valor_alvo - meta.valor_atual
        if falta <= 0:
            return 0.0
        meses = FinancasService.meses_restantes(meta)
        if meses <= 0:
            return falta
        return falta / meses

    def status_metas(self) -> List[Dict]:
        resultado = []
        for m in self.listar_metas():
            progresso = self.progresso_meta(m)
            dias = self.dias_restantes(m)
            meses = self.meses_restantes(m)
            mensal = self.valor_mensal_necessario(m)

            if m.valor_atual >= m.valor_alvo:
                status = "concluida"
            elif dias < 0:
                status = "atrasada"
            else:
                status = "em_dia"

            resultado.append(
                {
                    "meta": m,
                    "nome": m.nome,
                    "progresso": progresso,
                    "dias_restantes": dias,
                    "meses_restantes": meses,
                    "valor_mensal_necessario": mensal,
                    "status": status,
                }
            )
        return resultado