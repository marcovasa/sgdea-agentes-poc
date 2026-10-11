from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import TipoPQRSDF


class RadicadoCrear(BaseModel):
    tipo: TipoPQRSDF
    asunto: str = Field(min_length=3, max_length=300)
    descripcion: str = Field(default="", max_length=5000)
    remitente: str = Field(min_length=3, max_length=200)
    fecha_radicacion: date | None = None

    @field_validator("remitente")
    @classmethod
    def validar_remitente(cls, v: str) -> str:
        v_limpio = v.strip()
        if len(v_limpio) < 3:
            raise ValueError("El remitente debe tener al menos 3 caracteres")
        return v_limpio


class RadicadoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    numero: str
    tipo: str
    asunto: str
    descripcion: str
    remitente: str | None
    estado: str
    fecha_radicacion: date
    fecha_vencimiento: date


class ListaRadicados(BaseModel):
    total: int
    items: list[RadicadoSalida]
