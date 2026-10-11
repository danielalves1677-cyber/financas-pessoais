from pathlib import Path

# Raiz do projeto: .../financas-pessoais
# __file__ = src/financas/config/settings.py
# parents[0] = config
# parents[1] = financas
# parents[2] = src
# parents[3] = financas-pessoais  <-- queremos essa
RAIZ_PROJETO = Path(__file__).resolve().parents[3]

PASTA_DADOS = RAIZ_PROJETO / "data"
ARQUIVO_TRANSACOES = PASTA_DADOS / "transacoes.json"

# Garante que a pasta existe
PASTA_DADOS.mkdir(parents=True, exist_ok=True)