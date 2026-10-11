from pathlib import Path
from typing import List

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from financas.models import Orcamento, Transacao

from .db_models import Base, OrcamentoDB, TransacaoDB


class SqliteTransacaoRepository:
    """Repositório SQLite para transações e orçamentos."""

    def __init__(self, caminho: Path | str):
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)

        url = f"sqlite:///{self.caminho.as_posix()}"
        self.engine = create_engine(url, echo=False)
        Base.metadata.create_all(self.engine)

    # ---------- Conversões ----------
    @staticmethod
    def _db_para_model(db: TransacaoDB) -> Transacao:
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
        return TransacaoDB(
            id=t.id,
            descricao=t.descricao,
            valor=t.valor,
            tipo=t.tipo.value,
            categoria=t.categoria,
            data=t.data,
        )

    # ---------- Transações ----------
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

    # ---------- Orçamentos ----------
    def listar_orcamentos(self) -> List[Orcamento]:
        with Session(self.engine) as session:
            stmt = select(OrcamentoDB).order_by(OrcamentoDB.categoria)
            return [
                Orcamento(
                    id=o.id,
                    categoria=o.categoria,
                    limite_mensal=o.limite_mensal,
                )
                for o in session.scalars(stmt)
            ]

    def salvar_orcamento(self, orcamento: Orcamento) -> None:
        """Upsert: cria se não existe, atualiza se já existe (por categoria)."""
        with Session(self.engine) as session:
            stmt = select(OrcamentoDB).where(
                OrcamentoDB.categoria == orcamento.categoria
            )
            existente = session.scalars(stmt).first()
            if existente is None:
                session.add(
                    OrcamentoDB(
                        id=orcamento.id,
                        categoria=orcamento.categoria,
                        limite_mensal=orcamento.limite_mensal,
                    )
                )
            else:
                existente.limite_mensal = orcamento.limite_mensal
            session.commit()

    def remover_orcamento(self, orcamento_id: str) -> bool:
        with Session(self.engine) as session:
            db = session.get(OrcamentoDB, orcamento_id)
            if db is None:
                return False
            session.delete(db)
            session.commit()
            return True