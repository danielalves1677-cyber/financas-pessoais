import json
from pathlib import Path
from typing import List

from financas.models import Transacao


class JsonTransacaoRepository:
    """Repositório que persiste transações em arquivo JSON.

    Responsabilidade única: ler e escrever transações no disco.
    Não sabe nada sobre regras de negócio.
    """

    def __init__(self, caminho: Path | str):
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        if not self.caminho.exists():
            self._escrever([])

    def _ler(self) -> List[dict]:
        """Lê o arquivo e retorna lista de dicts brutos."""
        try:
            with self.caminho.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _escrever(self, dados: List[dict]) -> None:
        """Escreve a lista de dicts no arquivo, formatada."""
        with self.caminho.open("w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def listar(self) -> List[Transacao]:
        """Retorna todas as transações do arquivo."""
        return [Transacao.from_dict(d) for d in self._ler()]

    def adicionar(self, transacao: Transacao) -> None:
        """Adiciona uma transação ao arquivo."""
        dados = self._ler()
        dados.append(transacao.to_dict())
        self._escrever(dados)

    def remover(self, transacao_id: str) -> bool:
        """Remove uma transação pelo ID.

        Retorna True se removeu, False se o ID não existia.
        """
        dados = self._ler()
        novos = [d for d in dados if d["id"] != transacao_id]
        if len(novos) == len(dados):
            return False
        self._escrever(novos)
        return True