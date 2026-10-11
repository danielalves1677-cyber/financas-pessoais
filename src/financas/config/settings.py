import os
from pathlib import Path

# Raiz do projeto: .../financas-pessoais
RAIZ_PROJETO = Path(__file__).resolve().parents[3]

PASTA_DADOS = RAIZ_PROJETO / "data"
ARQUIVO_TRANSACOES = PASTA_DADOS / "transacoes.json"
ARQUIVO_DB = PASTA_DADOS / "financas.db"

# Backend padrão: 'json' ou 'sqlite' (controlado por env var DB_BACKEND)
DB_BACKEND = os.getenv("DB_BACKEND", "sqlite").lower()

# Garante que a pasta existe
PASTA_DADOS.mkdir(parents=True, exist_ok=True)