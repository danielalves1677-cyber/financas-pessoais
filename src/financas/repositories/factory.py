import os
from pathlib import Path

from .json_repository import JsonTransacaoRepository
from .sqlite_repository import SqliteTransacaoRepository

BACKEND_JSON = "json"
BACKEND_SQLITE = "sqlite"


def criar_repositorio(
    backend: str | None = None,
    caminho_json: Path | str | None = None,
    caminho_db: Path | str | None = None,
):
    """Fábrica de repositórios.

    Escolhe JSON ou SQLite com base em (em ordem de prioridade):
    1. Parâmetro `backend` passado explicitamente
    2. Variável de ambiente DB_BACKEND
    3. Padrão: json
    """
    backend = (backend or os.getenv("DB_BACKEND", BACKEND_JSON)).lower()

    if backend == BACKEND_JSON:
        if caminho_json is None:
            raise ValueError("caminho_json é obrigatório para o backend JSON")
        return JsonTransacaoRepository(caminho_json)

    if backend == BACKEND_SQLITE:
        if caminho_db is None:
            raise ValueError("caminho_db é obrigatório para o backend SQLite")
        return SqliteTransacaoRepository(caminho_db)

    raise ValueError(
        f"Backend desconhecido: {backend!r}. Use 'json' ou 'sqlite'."
    )