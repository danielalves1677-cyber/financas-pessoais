from datetime import datetime

from financas.config import ARQUIVO_DB, ARQUIVO_TRANSACOES, DB_BACKEND
from financas.models import Meta, Orcamento, TipoTransacao, Transacao
from financas.relatorios import (
    grafico_comparativo_mensal,
    grafico_evolucao_saldo,
    grafico_pizza_categorias,
    grafico_progresso_metas,
    grafico_status_orcamentos,
)
from financas.repositories import criar_repositorio
from financas.services import FinancasService
from financas.utils import (
    formatar_data,
    formatar_moeda,
    ler_texto_obrigatorio,
    ler_valor_positivo,
)


class MenuCLI:
    """Interface de linha de comando do gerenciador financeiro."""

    def __init__(self):
        repo = criar_repositorio(
            backend=DB_BACKEND,
            caminho_json=ARQUIVO_TRANSACOES,
            caminho_db=ARQUIVO_DB,
        )
        self.service = FinancasService(repo)
        print(f"🔌 Backend ativo: {DB_BACKEND}")

    # ---------- Helpers ----------
    def _cabecalho(self, titulo: str) -> None:
        print("\n" + "=" * 50)
        print(f"  {titulo}")
        print("=" * 50)

    # ---------- Transações ----------
    def adicionar_receita(self) -> None:
        self._cabecalho("➕ Nova Receita")
        descricao = ler_texto_obrigatorio("Descrição: ")
        valor = ler_valor_positivo("Valor: R$ ")
        categoria = ler_texto_obrigatorio("Categoria: ")
        t = Transacao(
            descricao=descricao,
            valor=valor,
            tipo=TipoTransacao.RECEITA,
            categoria=categoria,
        )
        self.service.adicionar(t)
        print(f"✅ Receita '{descricao}' adicionada!")

    def adicionar_despesa(self) -> None:
        self._cabecalho("➖ Nova Despesa")
        descricao = ler_texto_obrigatorio("Descrição: ")
        valor = ler_valor_positivo("Valor: R$ ")
        categoria = ler_texto_obrigatorio("Categoria: ")
        t = Transacao(
            descricao=descricao,
            valor=valor,
            tipo=TipoTransacao.DESPESA,
            categoria=categoria,
        )
        self.service.adicionar(t)
        print(f"✅ Despesa '{descricao}' adicionada!")

    def listar_transacoes(self) -> None:
        self._cabecalho("📋 Transações")
        transacoes = self.service.listar()
        if not transacoes:
            print("Nenhuma transação cadastrada.")
            return
        for t in transacoes:
            sinal = "+" if t.tipo == TipoTransacao.RECEITA else "-"
            print(
                f"[{t.id[:8]}] {formatar_data(t.data)} | "
                f"{t.descricao[:25]:<25} | {t.categoria[:15]:<15} | "
                f"{sinal}{formatar_moeda(t.valor)}"
            )

    def mostrar_resumo(self) -> None:
        self._cabecalho("💼 Resumo")
        print(f"Receitas: {formatar_moeda(self.service.total_receitas())}")
        print(f"Despesas: {formatar_moeda(self.service.total_despesas())}")
        saldo = self.service.saldo()
        status = "✅ Positivo" if saldo >= 0 else "⚠️  Negativo"
        print(f"Saldo:    {formatar_moeda(saldo)}  {status}")

    def relatorio_categorias(self) -> None:
        self._cabecalho("📊 Por Categoria")
        dados = self.service.por_categoria()
        if not dados:
            print("Nenhum dado.")
            return
        for cat, valores in dados.items():
            print(f"\n📁 {cat}")
            print(f"   Receitas: {formatar_moeda(valores['receita'])}")
            print(f"   Despesas: {formatar_moeda(valores['despesa'])}")
            print(f"   Saldo:    {formatar_moeda(valores['saldo'])}")

    def remover_transacao(self) -> None:
        self._cabecalho("🗑️  Remover Transação")
        self.listar_transacoes()
        if not self.service.listar():
            return
        id_parcial = input("\nDigite os 8 primeiros caracteres do ID: ").strip()
        if not id_parcial:
            print("❌ Nada digitado.")
            return
        for t in self.service.listar():
            if t.id.startswith(id_parcial):
                if self.service.remover(t.id):
                    print(f"✅ Transação '{t.descricao}' removida!")
                return
        print("❌ Nenhuma transação encontrada com esse ID.")

    # ---------- Orçamentos ----------
    def definir_orcamento(self) -> None:
        self._cabecalho("🎯 Definir Orçamento")
        categoria = ler_texto_obrigatorio("Categoria: ")
        limite = ler_valor_positivo("Limite mensal: R$ ")
        orc = Orcamento(categoria=categoria, limite_mensal=limite)
        self.service.salvar_orcamento(orc)
        print(
            f"✅ Orçamento de '{categoria}' definido: "
            f"{formatar_moeda(limite)}/mês"
        )

    def ver_orcamentos(self) -> None:
        self._cabecalho("🎯 Status dos Orçamentos (mês atual)")
        status = self.service.status_orcamento()
        if not status:
            print("Nenhum orçamento definido.")
            return
        for s in status:
            emoji = {"ok": "✅", "alerta": "⚠️ ", "estourado": "🚨"}[s["status"]]
            print(f"\n{emoji} {s['categoria']}")
            print(f"   Gasto:    {formatar_moeda(s['gasto'])}")
            print(f"   Limite:   {formatar_moeda(s['limite'])}")
            print(f"   Uso:      {s['percentual']:.1f}%")

    def remover_orcamento(self) -> None:
        self._cabecalho("🗑️  Remover Orçamento")
        orcs = self.service.listar_orcamentos()
        if not orcs:
            print("Nenhum orçamento cadastrado.")
            return
        for o in orcs:
            print(f"[{o.id[:8]}] {o.categoria} — {formatar_moeda(o.limite_mensal)}")
        id_parcial = input("\n8 primeiros caracteres do ID: ").strip()
        if not id_parcial:
            print("❌ Nada digitado.")
            return
        for o in orcs:
            if o.id.startswith(id_parcial):
                if self.service.remover_orcamento(o.id):
                    print("✅ Orçamento removido!")
                return
        print("❌ Não encontrado.")

    # ---------- Metas ----------
    def criar_meta(self) -> None:
        self._cabecalho("🎯 Nova Meta")
        nome = ler_texto_obrigatorio("Nome da meta: ")
        valor_alvo = ler_valor_positivo("Valor alvo: R$ ")

        while True:
            try:
                data_str = input("Prazo (DD/MM/AAAA): ").strip()
                prazo = datetime.strptime(data_str, "%d/%m/%Y").date()
                if prazo < datetime.now().date():
                    print("❌ O prazo deve ser no futuro.")
                    continue
                break
            except ValueError:
                print("❌ Data inválida. Use o formato DD/MM/AAAA.")

        meta = Meta(nome=nome, valor_alvo=valor_alvo, prazo=prazo)
        self.service.salvar_meta(meta)
        print(
            f"✅ Meta '{nome}' criada! Alvo: {formatar_moeda(valor_alvo)} "
            f"até {data_str}"
        )

    def ver_metas(self) -> None:
        self._cabecalho("📈 Status das Metas")
        status = self.service.status_metas()
        if not status:
            print("Nenhuma meta cadastrada.")
            return
        for s in status:
            emoji = {
                "concluida": "🏆",
                "atrasada": "⚠️ ",
                "em_dia": "🎯",
            }[s["status"]]
            m = s["meta"]
            print(f"\n{emoji} {s['nome']}")
            print(
                f"   Progresso: {formatar_moeda(m.valor_atual)} / "
                f"{formatar_moeda(m.valor_alvo)} ({s['progresso']:.1f}%)"
            )
            pct = min(100, s["progresso"])
            preenchido = int(pct / 5)
            barra = "█" * preenchido + "░" * (20 - preenchido)
            print(f"   [{barra}]")
            print(
                f"   Prazo: {m.prazo.strftime('%d/%m/%Y')} "
                f"({s['dias_restantes']} dias)"
            )

            if s["status"] == "concluida":
                print("   ✅ Meta concluída! Parabéns!")
            elif s["status"] == "atrasada":
                falta = m.valor_alvo - m.valor_atual
                print(f"   ⚠️  ATRASADA! Falta {formatar_moeda(falta)}")
            else:
                print(
                    f"   💡 Guarde {formatar_moeda(s['valor_mensal_necessario'])}/mês"
                )

    def atualizar_meta(self) -> None:
        self._cabecalho("💰 Atualizar Progresso de Meta")
        metas = self.service.listar_metas()
        if not metas:
            print("Nenhuma meta cadastrada.")
            return
        for m in metas:
            print(
                f"[{m.id[:8]}] {m.nome} — "
                f"{formatar_moeda(m.valor_atual)} / {formatar_moeda(m.valor_alvo)}"
            )
        id_parcial = input("\n8 primeiros caracteres do ID: ").strip()
        meta = next((m for m in metas if m.id.startswith(id_parcial)), None)
        if meta is None:
            print("❌ Meta não encontrada.")
            return

        valor = ler_valor_positivo("Valor a adicionar: R$ ")
        meta.valor_atual += valor
        self.service.salvar_meta(meta)
        print(f"✅ Progresso atualizado: {formatar_moeda(meta.valor_atual)}")

    def remover_meta(self) -> None:
        self._cabecalho("🗑️  Remover Meta")
        metas = self.service.listar_metas()
        if not metas:
            print("Nenhuma meta cadastrada.")
            return
        for m in metas:
            print(f"[{m.id[:8]}] {m.nome}")
        id_parcial = input("\n8 primeiros caracteres do ID: ").strip()
        if not id_parcial:
            print("❌ Nada digitado.")
            return
        for m in metas:
            if m.id.startswith(id_parcial):
                if self.service.remover_meta(m.id):
                    print(f"✅ Meta '{m.nome}' removida!")
                return
        print("❌ Não encontrada.")

    # ---------- Gráficos ----------
    def gerar_grafico_evolucao(self) -> None:
        self._cabecalho("📊 Evolução do Saldo")
        caminho = grafico_evolucao_saldo(self.service.listar())
        print(f"✅ Gráfico salvo em: {caminho}")

    def gerar_pizza_categorias(self) -> None:
        self._cabecalho("🥧 Pizza de Despesas por Categoria")
        caminho = grafico_pizza_categorias(self.service.listar())
        print(f"✅ Gráfico salvo em: {caminho}")

    def gerar_comparativo_mensal(self) -> None:
        self._cabecalho("📈 Comparativo Mensal")
        caminho = grafico_comparativo_mensal(self.service.listar())
        print(f"✅ Gráfico salvo em: {caminho}")

    def gerar_grafico_metas(self) -> None:
        self._cabecalho("🎯 Progresso das Metas")
        caminho = grafico_progresso_metas(self.service.status_metas())
        print(f"✅ Gráfico salvo em: {caminho}")

    def gerar_grafico_orcamentos(self) -> None:
        self._cabecalho("📊 Status dos Orçamentos")
        caminho = grafico_status_orcamentos(self.service.status_orcamento())
        print(f"✅ Gráfico salvo em: {caminho}")

    # ---------- Loop principal ----------
    def executar(self) -> None:
        opcoes = {
            "1": ("➕ Adicionar Receita", self.adicionar_receita),
            "2": ("➖ Adicionar Despesa", self.adicionar_despesa),
            "3": ("📋 Listar Transações", self.listar_transacoes),
            "4": ("📊 Relatório por Categoria", self.relatorio_categorias),
            "5": ("💼 Ver Resumo", self.mostrar_resumo),
            "6": ("🗑️  Remover Transação", self.remover_transacao),
            "7": ("🎯 Definir Orçamento", self.definir_orcamento),
            "8": ("📈 Ver Orçamentos", self.ver_orcamentos),
            "9": ("🗑️  Remover Orçamento", self.remover_orcamento),
            "10": ("🎯 Criar Meta", self.criar_meta),
            "11": ("📈 Ver Metas", self.ver_metas),
            "12": ("💰 Atualizar Meta", self.atualizar_meta),
            "13": ("🗑️  Remover Meta", self.remover_meta),
            "14": ("📊 Gráfico: Evolução do Saldo", self.gerar_grafico_evolucao),
            "15": ("🥧 Gráfico: Pizza de Categorias", self.gerar_pizza_categorias),
            "16": ("📈 Gráfico: Comparativo Mensal", self.gerar_comparativo_mensal),
            "17": ("🎯 Gráfico: Progresso das Metas", self.gerar_grafico_metas),
            "18": ("📊 Gráfico: Status dos Orçamentos", self.gerar_grafico_orcamentos),
        }

        while True:
            self._cabecalho("💰 FINANÇAS PESSOAIS")
            for chave, (texto, _) in opcoes.items():
                print(f"  {chave}. {texto}")
            print("  0. 🚪 Sair")

            escolha = input("\nEscolha uma opção: ").strip()

            if escolha == "0":
                print("\n👋 Até logo!")
                break
            if escolha in opcoes:
                try:
                    opcoes[escolha][1]()
                except Exception as e:
                    print(f"❌ Erro inesperado: {e}")
            else:
                print("❌ Opção inválida.")