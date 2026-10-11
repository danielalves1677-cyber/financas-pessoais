"""Aba Metas: lista de metas com barra de progresso."""
from datetime import datetime

import customtkinter as ctk

from financas.models import Meta
from financas.utils import formatar_moeda


class MetasView:
    def __init__(self, parent, service, app):
        self.parent = parent
        self.service = service
        self.app = app

        ctk.CTkLabel(
            parent,
            text="📈 Metas Financeiras",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Formulário
        form = ctk.CTkFrame(parent)
        form.pack(fill="x", padx=20, pady=10)

        linha = ctk.CTkFrame(form, fg_color="transparent")
        linha.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(linha, text="Nome:").pack(side="left", padx=(0, 5))
        self.entry_nome = ctk.CTkEntry(linha, placeholder_text="Ex: Viagem", width=180)
        self.entry_nome.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(linha, text="Valor (R$):").pack(side="left", padx=(0, 5))
        self.entry_valor = ctk.CTkEntry(linha, placeholder_text="10000", width=110)
        self.entry_valor.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(linha, text="Prazo:").pack(side="left", padx=(0, 5))
        self.entry_prazo = ctk.CTkEntry(linha, placeholder_text="DD/MM/AAAA", width=130)
        self.entry_prazo.pack(side="left", padx=(0, 15))

        ctk.CTkButton(linha, text="🎯 Criar", command=self.criar, width=100).pack(side="left", padx=(0, 10))
        ctk.CTkButton(linha, text="🔄 Atualizar", command=self.atualizar, width=120, fg_color="gray").pack(side="left")

        # Lista
        self.frame_lista = ctk.CTkScrollableFrame(parent)
        self.frame_lista.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.atualizar()

    def criar(self) -> None:
        nome = self.entry_nome.get().strip()
        valor_str = self.entry_valor.get().strip().replace(",", ".")
        prazo_str = self.entry_prazo.get().strip()
        if not nome:
            return
        try:
            valor = float(valor_str)
            prazo = datetime.strptime(prazo_str, "%d/%m/%Y").date()
        except ValueError:
            return

        self.service.salvar_meta(Meta(nome=nome, valor_alvo=valor, prazo=prazo))
        self.entry_nome.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_prazo.delete(0, "end")
        self.atualizar()

    def atualizar(self) -> None:
        for w in self.frame_lista.winfo_children():
            w.destroy()

        status = self.service.status_metas()
        if not status:
            ctk.CTkLabel(self.frame_lista, text="Nenhuma meta cadastrada.", text_color="gray").pack(pady=20)
            return

        emoji_map = {"concluida": "🏆", "atrasada": "⚠️", "em_dia": "🎯"}
        cor_map = {"concluida": "#2ecc71", "atrasada": "#e74c3c", "em_dia": "#3498db"}

        for s in status:
            m = s["meta"]
            card = ctk.CTkFrame(self.frame_lista, fg_color="#2c3e50", corner_radius=8)
            card.pack(fill="x", pady=6, padx=5)

            ctk.CTkLabel(
                card,
                text=f"{emoji_map[s['status']]}  {s['nome']}",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=cor_map[s["status"]],
                anchor="w",
            ).pack(anchor="w", padx=15, pady=(10, 3))

            ctk.CTkLabel(
                card,
                text=(
                    f"{formatar_moeda(m.valor_atual)} / {formatar_moeda(m.valor_alvo)}  "
                    f"({s['progresso']:.1f}%)"
                ),
                anchor="w",
            ).pack(anchor="w", padx=15, pady=3)

            # Barra de progresso
            progressbar = ctk.CTkProgressBar(card, height=12)
            progressbar.pack(fill="x", padx=15, pady=(3, 5))
            progressbar.set(min(1.0, s["progresso"] / 100))

            ctk.CTkLabel(
                card,
                text=(
                    f"Prazo: {m.prazo.strftime('%d/%m/%Y')}  ({s['dias_restantes']} dias)  |  "
                    f"Guarde {formatar_moeda(s['valor_mensal_necessario'])}/mês"
                ),
                font=ctk.CTkFont(size=11),
                text_color="lightgray",
                anchor="w",
            ).pack(anchor="w", padx=15, pady=(0, 10))