from pathlib import Path
from typing import List

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from financas.models import Transacao

from .db_models import Base, TransacaoDB


class SqliteTransacaoRepository:
    """Repositório que persiste transações em banco SQLite via SQLAlchemy.

    Implementa a mesma interface do JsonTransacaoRepository:
    listar(), adicionar(), remover().
    """

    def __init__(self, caminho: Path | str):
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)

        # 'sqlite:///E:/caminho/db.sqlite' (3 barras = caminho absoluto)
        url = f"sqlite:///{self.caminho.as_posix()}"
        self.engine = create_engine(url, echo=False)

        # Cria as tabelas se não existirem
        Base.metadata.create_all(self.engine)

    # ---------- Conversões ----------
    @staticmethod
    def _db_para_model(db: TransacaoDB) -> Transacao:
        """Converte linha do banco para o modelo Pydantic."""
        return Transacao(
            id=db.id,
            descricao=db.descricao,
            valor=db.valor,
            tipo=db.tipo,
            categoria=db.categoria,
            data=db.data,
        )

    @staticmethod
    def _model_para_db(t: Transacao) -> TransacaoDB:
        """Converte modelo Pydantic para linha do banco."""
        return TransacaoDB(
            id=t.id,
            descricao=t.descricao,
            valor=t.valor,
            tipo=t.tipo.value,
            categoria=t.categoria,
            data=t.data,
        )

    # ---------- Interface pública ----------
    def listar(self) -> List[Transacao]:
        with Session(self.engine) as session:
            stmt = select(TransacaoDB).order_by(TransacaoDB.data)
            return [self._db_para_model(db) for db in session.scalars(stmt)]

    def adicionar(self, transacao: Transacao) -> None:
        with Session(self.engine) as session:
            session.add(self._model_para_db(transacao))
            session.commit()

    def remover(self, transacao_id: str) -> bool:
        with Session(self.engine) as session:
            db = session.get(TransacaoDB, transacao_id)
            if db is None:
                return False
            session.delete(db)
            session.commit()
            return True