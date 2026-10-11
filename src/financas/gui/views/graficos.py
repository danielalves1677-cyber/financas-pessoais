"""Aba Gráficos: gera e visualiza os PNGs."""
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from financas.relatorios import (
    grafico_comparativo_mensal,
    grafico_evolucao_saldo,
    grafico_pizza_categorias,
    grafico_progresso_metas,
    grafico_status_orcamentos,
)


class GraficosView:
    def __init__(self, parent, service, app):
        self.parent = parent
        self.service = service
        self.app = app

        ctk.CTkLabel(
            parent,
            text="📊 Gráficos",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Botões de geração
        botoes = ctk.CTkFrame(parent, fg_color="transparent")
        botoes.pack(fill="x", padx=20, pady=10)

        opcoes = [
            ("📈 Evolução Saldo", self.gerar_evolucao),
            ("🥧 Pizza Categorias", self.gerar_pizza),
            ("📊 Comparativo Mensal", self.gerar_comparativo),
            ("🎯 Progresso Metas", self.gerar_metas),
            ("📋 Status Orçamentos", self.gerar_orcamentos),
        ]
        for texto, cmd in opcoes:
            ctk.CTkButton(botoes, text=texto, command=cmd, width=170).pack(side="left", padx=5)

        # Área da imagem
        self.frame_img = ctk.CTkFrame(parent)
        self.frame_img.pack(fill="both", expand=True, padx=20, pady=10)

        self.label_img = ctk.CTkLabel(
            self.frame_img,
            text="Clique em um botão acima para gerar um gráfico.",
            text_color="gray",
        )
        self.label_img.pack(expand=True)

        self._ultimo_caminho: Path | None = None

    def gerar_evolucao(self) -> None:
        self._gerar_com_seguranca(grafico_evolucao_saldo, self.service.listar())

    def gerar_pizza(self) -> None:
        self._gerar_com_seguranca(grafico_pizza_categorias, self.service.listar())

    def gerar_comparativo(self) -> None:
        self._gerar_com_seguranca(grafico_comparativo_mensal, self.service.listar())

    def gerar_metas(self) -> None:
        self._gerar_com_seguranca(grafico_progresso_metas, self.service.status_metas())

    def gerar_orcamentos(self) -> None:
        self._gerar_com_seguranca(grafico_status_orcamentos, self.service.status_orcamento())

    def _gerar_com_seguranca(self, funcao, argumento) -> None:
        """Gera o gráfico tratando possíveis erros."""
        try:
            caminho = funcao(argumento)
            self._ultimo_caminho = caminho
            self._mostrar_imagem(caminho)
        except Exception as e:
            # Mostra o erro amigavelmente em vez de travar a GUI
            self.label_img.configure(
                image=None,
                text=f"❌ Erro ao gerar gráfico:\n{e}\n\n"
                     "Dica: feche visualizadores de imagem abertos e tente novamente.",
                text_color="#e74c3c",
            )

    def _mostrar_imagem(self, caminho: Path) -> None:
        """Carrega o PNG e exibe na área."""
        try:
            img = Image.open(caminho)

            # Redimensiona pra caber
            largura_max = 900
            altura_max = 450
            img.thumbnail((largura_max, altura_max), Image.LANCZOS)

            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.label_img.configure(image=ctk_img, text="")
            self.label_img.image = ctk_img  # mantém referência
        except Exception as e:
            self.label_img.configure(
                image=None,
                text=f"Erro ao carregar imagem: {e}",
                text_color="#e74c3c",
            )

    def atualizar(self) -> None:
        """Se já houver um gráfico, recarrega."""
        if self._ultimo_caminho and self._ultimo_caminho.exists():
            self._mostrar_imagem(self._ultimo_caminho)