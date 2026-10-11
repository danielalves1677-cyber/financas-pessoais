from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class TipoTransacao(str, Enum):
    """Tipos possíveis de transação financeira."""
    RECEITA = "receita"
    DESPESA = "despesa"


class Transacao(BaseModel):
    """Representa uma transação financeira (receita ou despesa).

    Usa Pydantic para validação automática dos campos.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    descricao: str = Field(..., min_length=1, max_length=200)
    valor: float = Field(..., gt=0, description="Valor deve ser maior que zero")
    tipo: TipoTransacao
    categoria: str = Field(..., min_length=1, max_length=50)
    data: datetime = Field(default_factory=datetime.now)

    @field_validator("descricao", "categoria")
    @classmethod
    def nao_pode_ser_vazio(cls, v: str) -> str:
        """Remove espaços extras e rejeita strings vazias."""
        v = v.strip()
        if not v:
            raise ValueError("Campo não pode ser vazio")
        return v

    def to_dict(self) -> dict:
        """Serializa a transação para dicionário (usado na persistência)."""
        return {
            "id": self.id,
            "descricao": self.descricao,
            "valor": self.valor,
            "tipo": self.tipo.value,
            "categoria": self.categoria,
            "data": self.data.isoformat(),
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Transacao":
        """Reconstrói uma Transacao a partir de um dicionário."""
        return cls(**dados)