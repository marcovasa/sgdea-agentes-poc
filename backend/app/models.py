from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class TipoPQRSDF(StrEnum):
    PETICION = "PETICION"
    QUEJA = "QUEJA"
    RECLAMO = "RECLAMO"
    SUGERENCIA = "SUGERENCIA"
    DENUNCIA = "DENUNCIA"
    CONSULTA = "CONSULTA"
    INFORMACION = "INFORMACION"


class EstadoRadicado(StrEnum):
    RADICADO = "RADICADO"
    EN_TRAMITE = "EN_TRAMITE"
    RESPONDIDO = "RESPONDIDO"
    ANULADO = "ANULADO"


class Radicado(Base):
    __tablename__ = "radicados"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    tipo: Mapped[str] = mapped_column(String(20))
    asunto: Mapped[str] = mapped_column(String(300))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    remitente: Mapped[str | None] = mapped_column(String(200), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default=EstadoRadicado.RADICADO)
    fecha_radicacion: Mapped[date] = mapped_column(Date)
    fecha_vencimiento: Mapped[date] = mapped_column(Date)
    motivo_anulacion: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    fecha_anulacion: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
