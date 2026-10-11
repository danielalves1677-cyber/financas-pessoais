"""Janela principal da aplicação GUI (CustomTkinter)."""
import customtkinter as ctk

from financas.config import ARQUIVO_DB, ARQUIVO_TRANSACOES, DB_BACKEND
from financas.repositories import criar_repositorio
from financas.services import FinancasService

from .views.dashboard import DashboardView
from .views.graficos import GraficosView
from .views.metas import MetasView
from .views.orcamentos import OrcamentosView
from .views.transacoes import TransacoesView


class FinancasApp(ctk.CTk):
    """Aplicação principal com abas."""

    def __init__(self):
        super().__init__()

        # ---------- Serviço ----------
        repo = criar_repositorio(
            backend=DB_BACKEND,
            caminho_json=ARQUIVO_TRANSACOES,
            caminho_db=ARQUIVO_DB,
        )
        self.service = FinancasService(repo)

        # ---------- Configuração da janela ----------
        self.title(f"💰 Finanças Pessoais — backend: {DB_BACKEND}")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Tema claro/escuro
        ctk.set_appearance_mode("dark")  # ou "light"
        ctk.set_default_color_theme("blue")

        # ---------- Tabs ----------
        self.tabs = ctk.CTkTabview(self, corner_radius=10)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=15)

        self.tab_dashboard = self.tabs.add("🏠 Dashboard")
        self.tab_transacoes = self.tabs.add("📋 Transações")
        self.tab_orcamentos = self.tabs.add("🎯 Orçamentos")
        self.tab_metas = self.tabs.add("📈 Metas")
        self.tab_graficos = self.tabs.add("📊 Gráficos")

        # ---------- Views ----------
        # Cada view recebe a tab onde vive e o service (dependency injection)
        self.view_dashboard = DashboardView(self.tab_dashboard, self.service, self)
        self.view_transacoes = TransacoesView(self.tab_transacoes, self.service, self)
        self.view_orcamentos = OrcamentosView(self.tab_orcamentos, self.service, self)
        self.view_metas = MetasView(self.tab_metas, self.service, self)
        self.view_graficos = GraficosView(self.tab_graficos, self.service, self)

        # ---------- Bind de evento ----------
        # Quando muda de aba, atualiza os dados da aba alvo
        self.tabs.configure(command=self._on_tab_change)

    def _on_tab_change(self) -> None:
        """Recarrega dados da aba selecionada."""
        atual = self.tabs.get()

        if atual == "🏠 Dashboard":
            self.view_dashboard.atualizar()
        elif atual == "📋 Transações":
            self.view_transacoes.atualizar()
        elif atual == "🎯 Orçamentos":
            self.view_orcamentos.atualizar()
        elif atual == "📈 Metas":
            self.view_metas.atualizar()
        elif atual == "📊 Gráficos":
            self.view_graficos.atualizar()


def main() -> None:
    """Ponto de entrada da GUI."""
    app = FinancasApp()
    app.mainloop()


if __name__ == "__main__":
    main()