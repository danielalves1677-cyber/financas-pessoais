import json
from pathlib import Path
from typing import List

from financas.models import Meta, Orcamento, Transacao


class JsonTransacaoRepository:
    """Repositório que persiste transações, orçamentos e metas em JSON."""

    def __init__(self, caminho: Path | str):
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        if not self.caminho.exists():
            self._escrever([])

        # Arquivo de orçamentos
        self.caminho_orcamentos = self.caminho.with_name(
            self.caminho.stem + "_orcamentos.json"
        )
        if not self.caminho_orcamentos.exists():
            self._escrever_orcamentos([])

        # Arquivo de metas
        self.caminho_metas = self.caminho.with_name(
            self.caminho.stem + "_metas.json"
        )
        if not self.caminho_metas.exists():
            self._escrever_metas([])

    # ---------- Transações ----------
    def _ler(self) -> List[dict]:
        try:
            with self.caminho.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _escrever(self, dados: List[dict]) -> None:
        with self.caminho.open("w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def listar(self) -> List[Transacao]:
        return [Transacao.from_dict(d) for d in self._ler()]

    def adicionar(self, transacao: Transacao) -> None:
        dados = self._ler()
        dados.append(transacao.to_dict())
        self._escrever(dados)

    def remover(self, transacao_id: str) -> bool:
        dados = self._ler()
        novos = [d for d in dados if d["id"] != transacao_id]
        if len(novos) == len(dados):
            return False
        self._escrever(novos)
        return True

    # ---------- Orçamentos ----------
    def _ler_orcamentos(self) -> List[dict]:
        try:
            with self.caminho_orcamentos.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _escrever_orcamentos(self, dados: List[dict]) -> None:
        with self.caminho_orcamentos.open("w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def listar_orcamentos(self) -> List[Orcamento]:
        return [Orcamento.from_dict(d) for d in self._ler_orcamentos()]

    def salvar_orcamento(self, orcamento: Orcamento) -> None:
        dados = self._ler_orcamentos()
        dados = [d for d in dados if d["categoria"] != orcamento.categoria]
        dados.append(orcamento.to_dict())
        self._escrever_orcamentos(dados)

    def remover_orcamento(self, orcamento_id: str) -> bool:
        dados = self._ler_orcamentos()
        novos = [d for d in dados if d["id"] != orcamento_id]
        if len(novos) == len(dados):
            return False
        self._escrever_orcamentos(novos)
        return True

    # ---------- Metas ----------
    def _ler_metas(self) -> List[dict]:
        try:
            with self.caminho_metas.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _escrever_metas(self, dados: List[dict]) -> None:
        with self.caminho_metas.open("w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def listar_metas(self) -> List[Meta]:
        return [Meta.from_dict(d) for d in self._ler_metas()]

    def salvar_meta(self, meta: Meta) -> None:
        dados = self._ler_metas()
        dados = [d for d in dados if d["id"] != meta.id]
        dados.append(meta.to_dict())
        self._escrever_metas(dados)

    def remover_meta(self, meta_id: str) -> bool:
        dados = self._ler_metas()
        novos = [d for d in dados if d["id"] != meta_id]
        if len(novos) == len(dados):
            return False
        self._escrever_metas(novos)
        return True