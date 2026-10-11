"""Aplicação web em Streamlit para Finanças Pessoais.

Executar com:
    streamlit run src/financas/web/app.py

Ou via módulo:
    python -m financas.web
"""
import sys
from datetime import date, datetime
from pathlib import Path

# ==========================================================
# AJUSTE DE PATH (necessário para o Streamlit Cloud)
# ==========================================================
# Garante que o pacote 'financas' (em src/) seja encontrado
_raiz = Path(__file__).resolve().parents[3]  # .../financas-pessoais
_src = _raiz / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

# ==========================================================
# Imports do projeto e de terceiros
# ==========================================================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from financas.config import ARQUIVO_DB, ARQUIVO_TRANSACOES, DB_BACKEND
from financas.models import Meta, Orcamento, TipoTransacao, Transacao
from financas.repositories import criar_repositorio
from financas.services import FinancasService
from financas.utils import formatar_moeda


# ==========================================================
# Configuração da página
# ==========================================================
st.set_page_config(
    page_title="Finanças Pessoais",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==========================================================
# Serviço (cacheado pra não recriar a cada interação)
# ==========================================================
@st.cache_resource
def get_service() -> FinancasService:
    """Cria o FinancasService uma vez por sessão."""
    repo = criar_repositorio(
        backend=DB_BACKEND,
        caminho_json=ARQUIVO_TRANSACOES,
        caminho_db=ARQUIVO_DB,
    )
    return FinancasService(repo)


def limpar_cache():
    """Limpa o cache do Streamlit (força recarregar dados)."""
    st.cache_data.clear()
    st.cache_resource.clear()


service = get_service()


# ==========================================================
# CSS personalizado
# ==========================================================
st.markdown(
    """
    <style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .metric-title { font-size: 14px; opacity: 0.85; margin-bottom: 8px; }
    .metric-value { font-size: 28px; font-weight: bold; }
    .stMetric { background-color: #262730; padding: 15px; border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# Header
# ==========================================================
col1, col2 = st.columns([4, 1])
with col1:
    st.title("💰 Finanças Pessoais")
    st.caption(f"Backend: **{DB_BACKEND}**")
with col2:
    if st.button("🔄 Recarregar dados", use_container_width=True):
        limpar_cache()
        st.rerun()

st.divider()


# ==========================================================
# Abas
# ==========================================================
tab_dash, tab_trans, tab_orc, tab_metas, tab_graf = st.tabs(
    ["🏠 Painel de controle", "📋 Transações", "🎯 Orçamentos", "📈 Metas", "📊 Gráficos"]
)


# ==========================================================
# ABA 1 — Dashboard
# ==========================================================
with tab_dash:
    st.header("🏠 Visão Geral")

    saldo = service.saldo()
    receitas = service.total_receitas()
    despesas = service.total_despesas()

    c1, c2, c3 = st.columns(3)
    c1.metric("💼 Saldo", formatar_moeda(saldo))
    c2.metric("💵 Receitas", formatar_moeda(receitas))
    c3.metric("💸 Despesas", formatar_moeda(despesas), delta=None)

    st.divider()

    # Resumo por categoria (tabela + gráfico)
    st.subheader("📁 Distribuição por Categoria")
    dados_cat = service.por_categoria()

    if dados_cat:
        df = pd.DataFrame(
            [
                {
                    "Categoria": cat,
                    "Receitas": vals["receita"],
                    "Despesas": vals["despesa"],
                    "Saldo": vals["saldo"],
                }
                for cat, vals in dados_cat.items()
            ]
        )
        df = df.sort_values("Despesas", ascending=False)

        col_tabela, col_grafico = st.columns([1, 1])
        with col_tabela:
            st.dataframe(
                df.style.format(
                    {"Receitas": "R$ {:.2f}", "Despesas": "R$ {:.2f}", "Saldo": "R$ {:.2f}"}
                ),
                use_container_width=True,
                hide_index=True,
            )
        with col_grafico:
            df_desp = df[df["Despesas"] > 0]
            if not df_desp.empty:
                fig = px.pie(
                    df_desp,
                    values="Despesas",
                    names="Categoria",
                    title="Despesas por Categoria",
                    hole=0.4,
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="white",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem despesas registradas ainda.")
    else:
        st.info("Nenhuma transação cadastrada. Vá para a aba **📋 Transações**.")

    st.divider()

    # Últimas 5 transações
    st.subheader("🕐 Últimas Transações")
    todas = service.listar()
    if todas:
        ultimas = sorted(todas, key=lambda t: t.data, reverse=True)[:5]
        df_ult = pd.DataFrame(
            [
                {
                    "Data": t.data.strftime("%d/%m/%Y %H:%M"),
                    "Descrição": t.descricao,
                    "Categoria": t.categoria,
                    "Tipo": "Receita" if t.tipo == TipoTransacao.RECEITA else "Despesa",
                    "Valor": f"{'+' if t.tipo == TipoTransacao.RECEITA else '-'} {formatar_moeda(t.valor)}",
                }
                for t in ultimas
            ]
        )
        st.dataframe(df_ult, use_container_width=True, hide_index=True)
    else:
        st.info("Sem transações recentes.")


# ==========================================================
# ABA 2 — Transações
# ==========================================================
with tab_trans:
    st.header("📋 Transações")

    # -------- Formulário --------
    with st.form("form_nova_transacao", clear_on_submit=True):
        st.subheader("➕ Nova Transação")
        c1, c2 = st.columns([1, 3])
        with c1:
            tipo_str = st.selectbox("Tipo", ["Receita", "Despesa"])
        with c2:
            descricao = st.text_input("Descrição", placeholder="Ex: Salário")

        c3, c4 = st.columns([1, 3])
        with c3:
            valor_str = st.text_input("Valor (R$)", placeholder="1000,00")
        with c4:
            categoria = st.text_input("Categoria", placeholder="Ex: Trabalho")

        submitted = st.form_submit_button("✅ Adicionar", use_container_width=True)

        if submitted:
            erros = []
            if not descricao.strip():
                erros.append("Descrição é obrigatória.")
            if not categoria.strip():
                erros.append("Categoria é obrigatória.")

            valor = 0.0
            try:
                valor = float(valor_str.strip().replace(",", "."))
                if valor <= 0:
                    raise ValueError
            except ValueError:
                erros.append("Valor deve ser um número maior que zero.")

            if erros:
                for e in erros:
                    st.error(f"❌ {e}")
            else:
                tipo = (
                    TipoTransacao.RECEITA
                    if tipo_str == "Receita"
                    else TipoTransacao.DESPESA
                )
                service.adicionar(
                    Transacao(
                        descricao=descricao.strip(),
                        valor=valor,
                        tipo=tipo,
                        categoria=categoria.strip(),
                    )
                )
                st.success(f"✅ '{descricao}' adicionada com sucesso!")
                st.rerun()

    st.divider()

    # -------- Tabela --------
    st.subheader("📊 Histórico")

    transacoes = service.listar()

    if not transacoes:
        st.info("Nenhuma transação cadastrada ainda.")
    else:
        # Filtro
        categorias = sorted({t.categoria for t in transacoes})
        col_f1, col_f2 = st.columns([2, 3])
        with col_f1:
            filtro_tipo = st.selectbox("Filtrar por tipo", ["Todas", "Receita", "Despesa"])
        with col_f2:
            filtro_cat = st.multiselect(
                "Filtrar por categoria",
                options=categorias,
                default=[],
            )

        filtradas = transacoes
        if filtro_tipo == "Receita":
            filtradas = [t for t in filtradas if t.tipo == TipoTransacao.RECEITA]
        elif filtro_tipo == "Despesa":
            filtradas = [t for t in filtradas if t.tipo == TipoTransacao.DESPESA]
        if filtro_cat:
            filtradas = [t for t in filtradas if t.categoria in filtro_cat]

        filtradas = sorted(filtradas, key=lambda t: t.data, reverse=True)

        # Tabela com botão de remover
        for i, t in enumerate(filtradas):
            cols = st.columns([1, 3, 2, 1, 2, 0.7])
            cols[0].write(t.data.strftime("%d/%m %H:%M"))
            cols[1].write(f"**{t.descricao}**")
            cols[2].write(t.categoria)
            if t.tipo == TipoTransacao.RECEITA:
                cols[3].markdown(":green[Receita]")
                cols[4].markdown(f":green[+ {formatar_moeda(t.valor)}]")
            else:
                cols[3].markdown(":red[Despesa]")
                cols[4].markdown(f":red[- {formatar_moeda(t.valor)}]")
            if cols[5].button("🗑️", key=f"del_t_{t.id}"):
                service.remover(t.id)
                st.rerun()


# ==========================================================
# ABA 3 — Orçamentos
# ==========================================================
with tab_orc:
    st.header("🎯 Orçamentos Mensais")

    # -------- Formulário --------
    with st.form("form_orcamento", clear_on_submit=True):
        st.subheader("➕ Definir Orçamento")
        c1, c2 = st.columns([3, 2])
        with c1:
            cat_orc = st.text_input("Categoria", placeholder="Ex: Alimentação")
        with c2:
            limite_str = st.text_input("Limite mensal (R$)", placeholder="800,00")

        submitted_orc = st.form_submit_button("✅ Definir", use_container_width=True)

        if submitted_orc:
            erros = []
            if not cat_orc.strip():
                erros.append("Categoria é obrigatória.")
            try:
                limite = float(limite_str.strip().replace(",", "."))
                if limite <= 0:
                    raise ValueError
            except ValueError:
                erros.append("Limite deve ser um número maior que zero.")

            if erros:
                for e in erros:
                    st.error(f"❌ {e}")
            else:
                service.salvar_orcamento(
                    Orcamento(categoria=cat_orc.strip(), limite_mensal=limite)
                )
                st.success(f"✅ Orçamento de '{cat_orc}' definido!")
                st.rerun()

    st.divider()

    # -------- Lista --------
    status_orc = service.status_orcamento()

    if not status_orc:
        st.info("Nenhum orçamento definido ainda.")
    else:
        for s in status_orc:
            with st.container(border=True):
                emoji = {"ok": "✅", "alerta": "⚠️", "estourado": "🚨"}[s["status"]]
                cor = {"ok": "green", "alerta": "orange", "estourado": "red"}[s["status"]]
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                c1.markdown(f"### {emoji} {s['categoria']}")
                c2.metric("Gasto", formatar_moeda(s["gasto"]))
                c3.metric("Limite", formatar_moeda(s["limite"]))
                c4.markdown(f"### :{cor}[{s['percentual']:.1f}%]")

                # Barra de progresso
                progresso = min(1.0, s["percentual"] / 100)
                st.progress(progresso, text=f"{s['percentual']:.1f}% do orçamento usado")


# ==========================================================
# ABA 4 — Metas
# ==========================================================
with tab_metas:
    st.header("📈 Metas Financeiras")

    # -------- Formulário --------
    with st.form("form_meta", clear_on_submit=True):
        st.subheader("🎯 Nova Meta")
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            nome_meta = st.text_input("Nome", placeholder="Ex: Viagem Europa")
        with c2:
            valor_meta_str = st.text_input("Valor alvo (R$)", placeholder="15000,00")
        with c3:
            prazo_input = st.date_input(
                "Prazo",
                value=date.today().replace(year=date.today().year + 1),
                min_value=date.today(),
            )

        submitted_meta = st.form_submit_button("✅ Criar Meta", use_container_width=True)

        if submitted_meta:
            erros = []
            if not nome_meta.strip():
                erros.append("Nome é obrigatório.")
            try:
                valor_meta = float(valor_meta_str.strip().replace(",", "."))
                if valor_meta <= 0:
                    raise ValueError
            except ValueError:
                erros.append("Valor deve ser um número maior que zero.")

            if erros:
                for e in erros:
                    st.error(f"❌ {e}")
            else:
                service.salvar_meta(
                    Meta(
                        nome=nome_meta.strip(),
                        valor_alvo=valor_meta,
                        prazo=prazo_input,
                    )
                )
                st.success(f"✅ Meta '{nome_meta}' criada!")
                st.rerun()

    st.divider()

    # -------- Lista --------
    status_metas = service.status_metas()

    if not status_metas:
        st.info("Nenhuma meta cadastrada ainda.")
    else:
        for s in status_metas:
            m = s["meta"]
            with st.container(border=True):
                emoji = {"concluida": "🏆", "atrasada": "⚠️", "em_dia": "🎯"}[s["status"]]
                cor = {"concluida": "green", "atrasada": "red", "em_dia": "blue"}[s["status"]]

                c1, c2 = st.columns([3, 1])
                c1.markdown(f"### {emoji} {s['nome']}")
                c2.markdown(f"### :{cor}[{s['progresso']:.1f}%]")

                c1b, c2b, c3b = st.columns(3)
                c1b.metric("Atual", formatar_moeda(m.valor_atual))
                c2b.metric("Alvo", formatar_moeda(m.valor_alvo))
                c3b.metric("Prazo", m.prazo.strftime("%d/%m/%Y"))

                progresso = min(1.0, s["progresso"] / 100)
                st.progress(progresso)

                # Linha de detalhes + botões
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    if s["status"] == "concluida":
                        st.success("Meta concluída! Parabéns! 🎉")
                    elif s["status"] == "atrasada":
                        falta = m.valor_alvo - m.valor_atual
                        st.warning(
                            f"⚠️ Atrasada! Faltam {formatar_moeda(falta)} em {abs(s['dias_restantes'])} dias."
                        )
                    else:
                        st.info(
                            f"💡 Guarde {formatar_moeda(s['valor_mensal_necessario'])}/mês "
                            f"({s['dias_restantes']} dias restantes)"
                        )
                with col_b:
                    valor_add_str = st.text_input(
                        "Adicionar",
                        key=f"add_{m.id}",
                        placeholder="R$",
                        label_visibility="collapsed",
                    )
                with col_c:
                    if st.button("💰 Add", key=f"btn_add_{m.id}", use_container_width=True):
                        try:
                            valor_add = float(valor_add_str.strip().replace(",", "."))
                            if valor_add > 0:
                                m.valor_atual += valor_add
                                service.salvar_meta(m)
                                st.rerun()
                        except (ValueError, AttributeError):
                            st.error("Valor inválido")

                if st.button(f"🗑️ Remover meta '{m.nome}'", key=f"del_m_{m.id}"):
                    service.remover_meta(m.id)
                    st.rerun()


# ==========================================================
# ABA 5 — Gráficos
# ==========================================================
with tab_graf:
    st.header("📊 Gráficos Interativos")

    transacoes = service.listar()

    if not transacoes:
        st.info("Adicione transações para visualizar gráficos.")
    else:
        # -------- Gráfico 1: Evolução do saldo --------
        st.subheader("📈 Evolução do Saldo (últimos 6 meses)")

        # Agrupa por mês
        df_t = pd.DataFrame(
            [
                {
                    "data": t.data,
                    "valor": t.valor if t.tipo == TipoTransacao.RECEITA else -t.valor,
                    "tipo": t.tipo.value,
                }
                for t in transacoes
            ]
        )
        df_t["mes"] = df_t["data"].dt.to_period("M").astype(str)
        df_mes = df_t.groupby("mes")["valor"].sum().reset_index().sort_values("mes")
        df_mes["acumulado"] = df_mes["valor"].cumsum()

        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=df_mes["mes"],
                y=df_mes["acumulado"],
                mode="lines+markers",
                name="Saldo acumulado",
                line=dict(color="#3498db", width=3),
                fill="tozeroy",
                fillcolor="rgba(52, 152, 219, 0.2)",
            )
        )
        fig1.update_layout(
            title="Evolução do Saldo Acumulado",
            xaxis_title="Mês",
            yaxis_title="Saldo (R$)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=400,
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.divider()

        # -------- Gráfico 2: Pizza despesas --------
        col_p1, col_p2 = st.columns(2)

        with col_p1:
            st.subheader("🥧 Despesas por Categoria")
            df_desp = df_t[df_t["tipo"] == "despesa"]

            if not df_desp.empty:
                df_desp_agr = (
                    df_desp.assign(categoria=[t.categoria for t in transacoes if t.tipo == TipoTransacao.DESPESA])
                    .groupby("categoria")["valor"]
                    .sum()
                    .abs()
                    .reset_index()
                )
                fig2 = px.pie(
                    df_desp_agr,
                    values="valor",
                    names="categoria",
                    hole=0.45,
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="white",
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sem despesas registradas.")

        with col_p2:
            st.subheader("📊 Comparativo Mensal")
            df_rec = df_t[df_t["tipo"] == "receita"].groupby("mes")["valor"].sum().reset_index()
            df_rec["valor"] = df_rec["valor"].abs()
            df_rec.columns = ["mes", "receitas"]

            df_des = df_desp.groupby("mes")["valor"].sum().reset_index()
            df_des["valor"] = df_des["valor"].abs()
            df_des.columns = ["mes", "despesas"]

            df_comp = pd.merge(df_rec, df_des, on="mes", how="outer").fillna(0)

            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x=df_comp["mes"], y=df_comp["receitas"], name="Receitas", marker_color="#2ecc71"))
            fig3.add_trace(go.Bar(x=df_comp["mes"], y=df_comp["despesas"], name="Despesas", marker_color="#e74c3c"))
            fig3.update_layout(
                barmode="group",
                title="Receitas vs Despesas",
                xaxis_title="Mês",
                yaxis_title="Valor (R$)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )
            st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # -------- Gráfico 3: Status orçamentos --------
        st.subheader("🎯 Status dos Orçamentos (mês atual)")
        status_o = service.status_orcamento()
        if status_o:
            df_o = pd.DataFrame(
                [
                    {
                        "Categoria": s["categoria"],
                        "Uso (%)": s["percentual"],
                        "Status": s["status"],
                    }
                    for s in status_o
                ]
            )
            cores = {"ok": "#2ecc71", "alerta": "#f39c12", "estourado": "#e74c3c"}
            fig4 = px.bar(
                df_o,
                x="Categoria",
                y="Uso (%)",
                color="Status",
                color_discrete_map=cores,
                title="Uso do Orçamento por Categoria",
            )
            fig4.add_hline(y=80, line_dash="dash", line_color="#f39c12", annotation_text="Alerta 80%")
            fig4.add_hline(y=100, line_dash="dash", line_color="#e74c3c", annotation_text="Limite 100%")
            fig4.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Nenhum orçamento definido.")

        # -------- Gráfico 4: Progresso das metas --------
        st.subheader("📈 Progresso das Metas")
        status_m = service.status_metas()
        if status_m:
            df_m = pd.DataFrame(
                [
                    {
                        "Meta": s["nome"],
                        "Progresso": min(100, s["progresso"]),
                        "Status": s["status"],
                    }
                    for s in status_m
                ]
            )
            cores_m = {"concluida": "#2ecc71", "atrasada": "#e74c3c", "em_dia": "#3498db"}
            fig5 = px.bar(
                df_m,
                x="Progresso",
                y="Meta",
                orientation="h",
                color="Status",
                color_discrete_map=cores_m,
                title="Progresso das Metas (%)",
                range_x=[0, 105],
            )
            fig5.add_vline(x=100, line_dash="dash", line_color="gray")
            fig5.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("Nenhuma meta cadastrada.")