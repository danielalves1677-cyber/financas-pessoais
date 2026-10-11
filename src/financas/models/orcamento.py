from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Orcamento(BaseModel):
    """Orçamento mensal de uma categoria.

    Ex: 'Alimentacao' com limite de R$ 800/mês.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    categoria: str = Field(..., min_length=1, max_length=50)
    limite_mensal: float = Field(..., gt=0, description="Limite deve ser maior que zero")

    @field_validator("categoria")
    @classmethod
    def categoria_nao_vazia(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Categoria não pode ser vazia")
        return v

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "categoria": self.categoria,
            "limite_mensal": self.limite_mensal,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Orcamento":
        return cls(**dados)