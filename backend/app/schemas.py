from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import TipoPQRSDF


class RadicadoCrear(BaseModel):
    tipo: TipoPQRSDF
    asunto: str = Field(min_length=3, max_length=300)
    descripcion: str = Field(default="", max_length=5000)
    remitente: str | None = None
    fecha_radicacion: date | None = None


class RadicadoAnular(BaseModel):
    motivo: str = Field(min_length=10)

    @field_validator("motivo")
    @classmethod
    def validar_motivo(cls, v: str) -> str:
        v_limpio = v.strip()
        if len(v_limpio) < 10:
            raise ValueError("El motivo debe tener al menos 10 caracteres")
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
    motivo_anulacion: str | None = None
    fecha_anulacion: date | None = None


class ListaRadicados(BaseModel):
    total: int
    items: list[RadicadoSalida]
