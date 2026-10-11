from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarativa do SQLAlchemy 2.x."""
    pass


class TransacaoDB(Base):
    """Tabela 'transacoes' no banco de dados."""

    __tablename__ = "transacoes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    data: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<TransacaoDB {self.id[:8]} {self.descricao} R$ {self.valor}>"


class OrcamentoDB(Base):
    """Tabela 'orcamentos' no banco de dados."""

    __tablename__ = "orcamentos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    categoria: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    limite_mensal: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self) -> str:
        return f"<OrcamentoDB {self.categoria} R$ {self.limite_mensal}>"


class MetaDB(Base):
    """Tabela 'metas' no banco de dados."""

    __tablename__ = "metas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    valor_alvo: Mapped[float] = mapped_column(Float, nullable=False)
    valor_atual: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    prazo: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<MetaDB {self.nome} R$ {self.valor_atual}/{self.valor_alvo}>"