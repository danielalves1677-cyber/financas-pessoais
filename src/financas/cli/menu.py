from financas.config import ARQUIVO_DB, ARQUIVO_TRANSACOES, DB_BACKEND
from financas.models import TipoTransacao, Transacao
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

    # ---------- Ações ----------
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
        self._cabecalho("🗑️  Remover")
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

    # ---------- Loop principal ----------
    def executar(self) -> None:
        opcoes = {
            "1": ("➕ Adicionar Receita", self.adicionar_receita),
            "2": ("➖ Adicionar Despesa", self.adicionar_despesa),
            "3": ("📋 Listar Transações", self.listar_transacoes),
            "4": ("📊 Relatório por Categoria", self.relatorio_categorias),
            "5": ("💼 Ver Resumo", self.mostrar_resumo),
            "6": ("🗑️  Remover Transação", self.remover_transacao),
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