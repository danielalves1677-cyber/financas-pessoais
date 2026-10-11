"""Entry point para rodar o app web via python -m financas.web."""
import subprocess
import sys
from pathlib import Path


def main():
    """Inicia o Streamlit apontando para app.py."""
    app_path = Path(__file__).parent / "app.py"
    # Reexecuta o streamlit como subprocesso
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path)],
        check=False,
    )


if __name__ == "__main__":
    main()