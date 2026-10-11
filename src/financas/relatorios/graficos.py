"""Funções de geração de gráficos com matplotlib.

Cada função gera UMA imagem PNG em data/graficos/.
Não abre janela (usa backend 'Agg'), então funciona em qualquer ambiente.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")  # backend não-interativo (salva em arquivo)

import matplotlib.pyplot as plt

from financas.models import Meta, Transacao, TipoTransacao


# ---------- Configurações globais ----------
CORES = {
    "receita": "#2ecc71",   # verde
    "despesa": "#e74c3c",   # vermelho
    "saldo": "#3498db",     # azul
    "ok": "#2ecc71",
    "alerta": "#f39c12",
    "estourado": "#e74c3c",
    "concluida": "#2ecc71",
    "atrasada": "#e74c3c",
    "em_dia": "#3498db",
}

PALETA_PIZZA = [
    "#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
    "#1abc9c", "#e67e22", "#34495e", "#16a085", "#c0392b",
]


def _pasta_saida() -> Path:
    """Garante que data/graficos/ exista e retorna o caminho."""
    pasta = Path(__file__).resolve().parents[3] / "data" / "graficos"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


# ---------- 1. Evolução do saldo (linha) ----------
def grafico_evolucao_saldo(
    transacoes: List[Transacao],
    meses: int = 6,
) -> Path:
    """Gera gráfico de linha com o saldo acumulado mês a mês.

    Retorna o caminho do PNG gerado.
    """
    # Agrupa transações por (ano, mês)
    agora = datetime.now()
    dados: Dict[str, float] = {}

    # Cria os últimos N meses (mesmo que vazios)
    for i in range(meses - 1, -1, -1):
        ref = agora.replace(day=1)
        # Retrocede i meses
        ano = ref.year
        mes = ref.month - i
        while mes <= 0:
            mes += 12
            ano -= 1
        chave = f"{ano}-{mes:02d}"
        dados[chave] = 0.0

    # Soma cada transação no mês correspondente
    for t in transacoes:
        chave = f"{t.data.year}-{t.data.month:02d}"
        if chave not in dados:
            continue
        if t.tipo == TipoTransacao.RECEITA:
            dados[chave] += t.valor
        else:
            dados[chave] -= t.valor

    # Calcula saldo acumulado
    meses_ord = sorted(dados.keys())
    saldo_acumulado = []
    acum = 0.0
    for m in meses_ord:
        acum += dados[m]
        saldo_acumulado.append(acum)

    # Plota
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(meses_ord, saldo_acumulado, marker="o", color=CORES["saldo"], linewidth=2)
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_title("Evolução do Saldo (últimos meses)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Saldo (R$)")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()

    caminho = _pasta_saida() / "evolucao_saldo.png"
    fig.savefig(caminho, dpi=100)
    plt.close(fig)
    return caminho


# ---------- 2. Pizza de despesas por categoria ----------
def grafico_pizza_categorias(
    transacoes: List[Transacao],
    mes: int | None = None,
    ano: int | None = None,
) -> Path:
    """Gera pizza de despesas por categoria no mês atual (ou indicado)."""
    agora = datetime.now()
    mes = mes or agora.month
    ano = ano or agora.year

    por_categoria: Dict[str, float] = {}
    for t in transacoes:
        if t.tipo != TipoTransacao.DESPESA:
            continue
        if t.data.month != mes or t.data.year != ano:
            continue
        por_categoria[t.categoria] = por_categoria.get(t.categoria, 0.0) + t.valor

    fig, ax = plt.subplots(figsize=(8, 6))
    if not por_categoria:
        ax.text(0.5, 0.5, "Sem despesas no período",
                ha="center", va="center", fontsize=14, color="gray")
        ax.axis("off")
    else:
        labels = list(por_categoria.keys())
        valores = list(por_categoria.values())
        cores = PALETA_PIZZA[: len(labels)]
        ax.pie(
            valores,
            labels=labels,
            autopct="%1.1f%%",
            colors=cores,
            startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        )
        ax.set_title(
            f"Despesas por Categoria — {mes:02d}/{ano}",
            fontsize=14, fontweight="bold",
        )

    fig.tight_layout()
    caminho = _pasta_saida() / "pizza_categorias.png"
    fig.savefig(caminho, dpi=100)
    plt.close(fig)
    return caminho


# ---------- 3. Comparativo mensal (barras) ----------
def grafico_comparativo_mensal(
    transacoes: List[Transacao],
    meses: int = 6,
) -> Path:
    """Barras agrupadas: receita vs despesa dos últimos N meses."""
    agora = datetime.now()
    dados: Dict[str, Dict[str, float]] = {}

    for i in range(meses - 1, -1, -1):
        ref = agora.replace(day=1)
        ano = ref.year
        mes = ref.month - i
        while mes <= 0:
            mes += 12
            ano -= 1
        chave = f"{ano}-{mes:02d}"
        dados[chave] = {"receita": 0.0, "despesa": 0.0}

    for t in transacoes:
        chave = f"{t.data.year}-{t.data.month:02d}"
        if chave not in dados:
            continue
        dados[chave][t.tipo.value] += t.valor

    meses_ord = sorted(dados.keys())
    receitas = [dados[m]["receita"] for m in meses_ord]
    despesas = [dados[m]["despesa"] for m in meses_ord]

    x = range(len(meses_ord))
    largura = 0.4

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([i - largura / 2 for i in x], receitas, largura,
           label="Receitas", color=CORES["receita"])
    ax.bar([i + largura / 2 for i in x], despesas, largura,
           label="Despesas", color=CORES["despesa"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(meses_ord, rotation=45, ha="right")
    ax.set_title("Comparativo Mensal — Receitas vs Despesas",
                 fontsize=14, fontweight="bold")
    ax.set_ylabel("Valor (R$)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()

    caminho = _pasta_saida() / "comparativo_mensal.png"
    fig.savefig(caminho, dpi=100)
    plt.close(fig)
    return caminho


# ---------- 4. Progresso das metas (barras horizontais) ----------
def grafico_progresso_metas(status_metas: List[Dict]) -> Path:
    """Barras horizontais mostrando progresso (%) de cada meta."""
    fig, ax = plt.subplots(figsize=(10, max(3, len(status_metas) * 0.6)))

    if not status_metas:
        ax.text(0.5, 0.5, "Nenhuma meta cadastrada",
                ha="center", va="center", fontsize=14, color="gray")
        ax.axis("off")
    else:
        nomes = [s["nome"] for s in status_metas]
        progressos = [min(100, s["progresso"]) for s in status_metas]
        cores = [CORES[s["status"]] for s in status_metas]

        y = range(len(nomes))
        ax.barh(list(y), progressos, color=cores, edgecolor="white")
        ax.set_yticks(list(y))
        ax.set_yticklabels(nomes)
        ax.set_xlim(0, 105)
        ax.set_xlabel("Progresso (%)")
        ax.set_title("Progresso das Metas", fontsize=14, fontweight="bold")
        ax.axvline(100, color="gray", linestyle="--", linewidth=0.8)
        ax.grid(True, axis="x", alpha=0.3)

        # Anota o percentual em cada barra
        for i, (p, s) in enumerate(zip(progressos, status_metas)):
            ax.text(p + 1, i, f"{s['progresso']:.1f}%",
                    va="center", fontsize=9)

    fig.tight_layout()
    caminho = _pasta_saida() / "progresso_metas.png"
    fig.savefig(caminho, dpi=100)
    plt.close(fig)
    return caminho


# ---------- 5. Status dos orçamentos (barras verticais com cor) ----------
def grafico_status_orcamentos(status_orcamentos: List[Dict]) -> Path:
    """Barras verticais mostrando % de uso de cada orçamento."""
    fig, ax = plt.subplots(figsize=(10, 5))

    if not status_orcamentos:
        ax.text(0.5, 0.5, "Nenhum orçamento cadastrado",
                ha="center", va="center", fontsize=14, color="gray")
        ax.axis("off")
    else:
        cats = [s["categoria"] for s in status_orcamentos]
        percentuais = [min(120, s["percentual"]) for s in status_orcamentos]
        cores = [CORES[s["status"]] for s in status_orcamentos]

        x = range(len(cats))
        ax.bar(list(x), percentuais, color=cores, edgecolor="white")
        ax.set_xticks(list(x))
        ax.set_xticklabels(cats, rotation=45, ha="right")
        ax.set_ylabel("Uso do orçamento (%)")
        ax.set_title("Status dos Orçamentos (mês atual)",
                     fontsize=14, fontweight="bold")
        ax.axhline(80, color="#f39c12", linestyle="--", linewidth=1,
                   label="Alerta (80%)")
        ax.axhline(100, color="#e74c3c", linestyle="--", linewidth=1,
                   label="Limite (100%)")
        ax.legend()
        ax.grid(True, axis="y", alpha=0.3)

        for i, p in enumerate(percentuais):
            ax.text(i, p + 1, f"{p:.0f}%", ha="center", fontsize=9)

    fig.tight_layout()
    caminho = _pasta_saida() / "status_orcamentos.png"
    fig.savefig(caminho, dpi=100)
    plt.close(fig)
    return caminho