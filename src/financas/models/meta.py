from datetime import date, datetime
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Meta(BaseModel):
    """Meta financeira com prazo.

    Ex: 'Viagem Europa' — R$ 15.000 até 30/06/2027.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    nome: str = Field(..., min_length=1, max_length=100)
    valor_alvo: float = Field(..., gt=0, description="Valor alvo deve ser > 0")
    valor_atual: float = Field(default=0.0, ge=0, description="Valor já guardado")
    prazo: date = Field(..., description="Data limite para atingir a meta")

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nome não pode ser vazio")
        return v

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "valor_alvo": self.valor_alvo,
            "valor_atual": self.valor_atual,
            "prazo": self.prazo.isoformat(),
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Meta":
        return cls(**dados)