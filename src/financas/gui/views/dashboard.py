"""Aba Dashboard: cards de resumo (saldo, receitas, despesas)."""
import customtkinter as ctk

from financas.utils import formatar_moeda


class DashboardView:
    """Painel com 3 cards grandes: Saldo, Receitas, Despesas."""

    def __init__(self, parent, service, app):
        self.parent = parent
        self.service = service
        self.app = app

        # Título
        ctk.CTkLabel(
            parent,
            text="📊 Visão Geral",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Container dos cards
        self.frame_cards = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame_cards.pack(fill="x", padx=20, pady=10)

        # 3 cards
        self.card_saldo = self._criar_card("💼 Saldo", "#3498db")
        self.card_receitas = self._criar_card("💵 Receitas", "#2ecc71")
        self.card_despesas = self._criar_card("💸 Despesas", "#e74c3c")

        # Botão de atualizar
        ctk.CTkButton(
            parent,
            text="🔄 Atualizar",
            command=self.atualizar,
            width=140,
        ).pack(pady=20)

        # Carrega os dados de início
        self.atualizar()

    def _criar_card(self, titulo: str, cor: str):
        """Cria um card bonito com título e valor."""
        card = ctk.CTkFrame(
            self.frame_cards,
            corner_radius=12,
            fg_color=cor,
            height=130,
        )
        card.pack(side="left", fill="both", expand=True, padx=8)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=titulo,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        valor_label = ctk.CTkLabel(
            card,
            text="R$ 0,00",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="white",
        )
        valor_label.pack(anchor="w", padx=15)

        return valor_label

    def atualizar(self) -> None:
        """Recarrega os valores do service."""
        saldo = self.service.saldo()
        receitas = self.service.total_receitas()
        despesas = self.service.total_despesas()

        self.card_saldo.configure(text=formatar_moeda(saldo))
        self.card_receitas.configure(text=formatar_moeda(receitas))
        self.card_despesas.configure(text=formatar_moeda(despesas))