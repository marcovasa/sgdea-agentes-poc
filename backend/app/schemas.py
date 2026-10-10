from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models import TipoPQRSDF


class RadicadoCrear(BaseModel):
    tipo: TipoPQRSDF
    asunto: str = Field(min_length=3, max_length=300)
    descripcion: str = Field(default="", max_length=5000)
    remitente: str | None = None
    fecha_radicacion: date | None = None


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
