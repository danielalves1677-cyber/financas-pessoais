from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
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