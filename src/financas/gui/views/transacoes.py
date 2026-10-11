"""Aba Transações: formulário + tabela de transações."""
import customtkinter as ctk
from tkinter import messagebox

from financas.models import Transacao, TipoTransacao
from financas.utils import formatar_data, formatar_moeda


class TransacoesView:
    """Lista e formulário de transações."""

    def __init__(self, parent, service, app):
        self.parent = parent
        self.service = service
        self.app = app

        ctk.CTkLabel(
            parent,
            text="📋 Transações",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # ---------- Formulário ----------
        frame_form = ctk.CTkFrame(parent)
        frame_form.pack(fill="x", padx=20, pady=10)

        # Linha 1: Tipo + Descrição
        linha1 = ctk.CTkFrame(frame_form, fg_color="transparent")
        linha1.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(linha1, text="Tipo:").pack(side="left", padx=(0, 5))
        self.combo_tipo = ctk.CTkComboBox(
            linha1, values=["Receita", "Despesa"], width=120, state="readonly"
        )
        self.combo_tipo.set("Receita")
        self.combo_tipo.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(linha1, text="Descrição:").pack(side="left", padx=(0, 5))
        self.entry_descricao = ctk.CTkEntry(linha1, placeholder_text="Ex: Salário")
        self.entry_descricao.pack(side="left", fill="x", expand=True, padx=(0, 20))

        ctk.CTkLabel(linha1, text="Valor (R$):").pack(side="left", padx=(0, 5))
        self.entry_valor = ctk.CTkEntry(linha1, placeholder_text="0,00", width=120)
        self.entry_valor.pack(side="left")

        # Linha 2: Categoria + Botões
        linha2 = ctk.CTkFrame(frame_form, fg_color="transparent")
        linha2.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkLabel(linha2, text="Categoria:").pack(side="left", padx=(0, 5))
        self.entry_categoria = ctk.CTkEntry(
            linha2, placeholder_text="Ex: Trabalho", width=200
        )
        self.entry_categoria.pack(side="left", padx=(0, 20))

        ctk.CTkButton(
            linha2, text="➕ Adicionar", command=self.adicionar, width=140
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            linha2,
            text="🔄 Atualizar",
            command=self.atualizar,
            width=120,
            fg_color="gray",
        ).pack(side="left")

        # ---------- Tabela ----------
        ctk.CTkLabel(
            parent,
            text="Histórico:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(15, 5))

        self.frame_tabela = ctk.CTkScrollableFrame(parent)
        self.frame_tabela.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.atualizar()

    def adicionar(self) -> None:
        """Lê os campos e cria uma nova transação."""
        tipo_str = self.combo_tipo.get()
        descricao = self.entry_descricao.get().strip()
        valor_str = self.entry_valor.get().strip().replace(",", ".")
        categoria = self.entry_categoria.get().strip()

        # Validação
        if not descricao or not categoria:
            messagebox.showerror("Erro", "Preencha descrição e categoria.")
            return

        try:
            valor = float(valor_str)
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Use algo como 100 ou 25,50.")
            return

        tipo = TipoTransacao.RECEITA if tipo_str == "Receita" else TipoTransacao.DESPESA

        transacao = Transacao(
            descricao=descricao,
            valor=valor,
            tipo=tipo,
            categoria=categoria,
        )
        self.service.adicionar(transacao)

        # Limpa o formulário
        self.entry_descricao.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_categoria.delete(0, "end")

        self.atualizar()

        # Avisa o dashboard pra atualizar
        self.app.view_dashboard.atualizar()

    def atualizar(self) -> None:
        """Recarrega a lista de transações na tabela."""
        # Limpa tabela
        for widget in self.frame_tabela.winfo_children():
            widget.destroy()

        transacoes = self.service.listar()

        if not transacoes:
            ctk.CTkLabel(
                self.frame_tabela,
                text="Nenhuma transação cadastrada ainda.",
                text_color="gray",
            ).pack(pady=20)
            return

        # Cabeçalho
        header = ctk.CTkFrame(self.frame_tabela, fg_color="#2c3e50", corner_radius=5)
        header.pack(fill="x", pady=(0, 2))
        self._celula(header, "Data", 0, bold=True)
        self._celula(header, "Descrição", 1, bold=True)
        self._celula(header, "Categoria", 2, bold=True)
        self._celula(header, "Tipo", 3, bold=True)
        self._celula(header, "Valor", 4, bold=True)

        # Linhas
        for i, t in enumerate(transacoes):
            cor = "#34495e" if i % 2 == 0 else "#2c3e50"
            linha = ctk.CTkFrame(self.frame_tabela, fg_color=cor, corner_radius=5)
            linha.pack(fill="x", pady=1)

            self._celula(linha, formatar_data(t.data), 0)
            self._celula(linha, t.descricao, 1)
            self._celula(linha, t.categoria, 2)

            tipo_txt = "Receita" if t.tipo == TipoTransacao.RECEITA else "Despesa"
            cor_tipo = "#2ecc71" if t.tipo == TipoTransacao.RECEITA else "#e74c3c"
            self._celula(linha, tipo_txt, 3, cor_texto=cor_tipo)

            sinal = "+" if t.tipo == TipoTransacao.RECEITA else "-"
            self._celula(linha, f"{sinal} {formatar_moeda(t.valor)}", 4, cor_texto=cor_tipo)

    def _celula(self, parent, texto, coluna, bold=False, cor_texto=None):
        """Cria uma 'célula' da tabela."""
        label = ctk.CTkLabel(
            parent,
            text=texto,
            anchor="w",
            font=ctk.CTkFont(size=12, weight="bold" if bold else "normal"),
            text_color=cor_texto or "white",
        )
        # Grid com pesos diferentes por coluna
        parent.grid_columnconfigure(0, weight=2)
        parent.grid_columnconfigure(1, weight=4)
        parent.grid_columnconfigure(2, weight=2)
        parent.grid_columnconfigure(3, weight=1)
        parent.grid_columnconfigure(4, weight=2)
        label.grid(row=0, column=coluna, sticky="w", padx=10, pady=6)