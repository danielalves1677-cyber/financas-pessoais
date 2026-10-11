"""Aba Orçamentos: lista de orçamentos com status."""
import customtkinter as ctk

from financas.models import Orcamento
from financas.utils import formatar_moeda


class OrcamentosView:
    def __init__(self, parent, service, app):
        self.parent = parent
        self.service = service
        self.app = app

        ctk.CTkLabel(
            parent,
            text="🎯 Orçamentos",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Formulário
        form = ctk.CTkFrame(parent)
        form.pack(fill="x", padx=20, pady=10)

        linha = ctk.CTkFrame(form, fg_color="transparent")
        linha.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(linha, text="Categoria:").pack(side="left", padx=(0, 5))
        self.entry_categoria = ctk.CTkEntry(linha, placeholder_text="Ex: Alimentação", width=200)
        self.entry_categoria.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(linha, text="Limite mensal (R$):").pack(side="left", padx=(0, 5))
        self.entry_limite = ctk.CTkEntry(linha, placeholder_text="500", width=120)
        self.entry_limite.pack(side="left", padx=(0, 20))

        ctk.CTkButton(linha, text="🎯 Definir", command=self.salvar, width=120).pack(side="left", padx=(0, 10))
        ctk.CTkButton(linha, text="🔄 Atualizar", command=self.atualizar, width=120, fg_color="gray").pack(side="left")

        # Lista
        self.frame_lista = ctk.CTkScrollableFrame(parent)
        self.frame_lista.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.atualizar()

    def salvar(self) -> None:
        categoria = self.entry_categoria.get().strip()
        limite_str = self.entry_limite.get().strip().replace(",", ".")
        if not categoria:
            return
        try:
            limite = float(limite_str)
            if limite <= 0:
                raise ValueError
        except ValueError:
            return

        self.service.salvar_orcamento(Orcamento(categoria=categoria, limite_mensal=limite))
        self.entry_categoria.delete(0, "end")
        self.entry_limite.delete(0, "end")
        self.atualizar()

    def atualizar(self) -> None:
        for w in self.frame_lista.winfo_children():
            w.destroy()

        status = self.service.status_orcamento()
        if not status:
            ctk.CTkLabel(self.frame_lista, text="Nenhum orçamento definido.", text_color="gray").pack(pady=20)
            return

        emoji_map = {"ok": "✅", "alerta": "⚠️", "estourado": "🚨"}
        cor_map = {"ok": "#2ecc71", "alerta": "#f39c12", "estourado": "#e74c3c"}

        for s in status:
            card = ctk.CTkFrame(self.frame_lista, fg_color="#2c3e50", corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(
                card,
                text=f"{emoji_map[s['status']]}  {s['categoria']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=cor_map[s["status"]],
                anchor="w",
            ).pack(anchor="w", padx=15, pady=(10, 5))

            ctk.CTkLabel(
                card,
                text=(
                    f"Gasto: {formatar_moeda(s['gasto'])}  |  "
                    f"Limite: {formatar_moeda(s['limite'])}  |  "
                    f"Uso: {s['percentual']:.1f}%"
                ),
                anchor="w",
            ).pack(anchor="w", padx=15, pady=(0, 10))