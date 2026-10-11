"""Reglas de negocio del módulo de radicación."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import EstadoRadicado, Radicado, TipoPQRSDF
from app.schemas import RadicadoCrear
from app.services.plazos import calcular_vencimiento

PREFIJO_TIPO: dict[TipoPQRSDF, str] = {
    TipoPQRSDF.PETICION: "P",
    TipoPQRSDF.QUEJA: "Q",
    TipoPQRSDF.RECLAMO: "R",
    TipoPQRSDF.SUGERENCIA: "S",
    TipoPQRSDF.DENUNCIA: "D",
    TipoPQRSDF.CONSULTA: "C",
    TipoPQRSDF.INFORMACION: "I",
}


def generar_numero(session: Session, tipo: TipoPQRSDF, fecha: date) -> str:
    """Número de radicado: AAAA-<prefijo tipo>-<consecutivo anual por tipo>."""
    prefijo = PREFIJO_TIPO[tipo]
    patron = f"{fecha.year}-{prefijo}-%"
    existentes = session.scalar(
        select(func.count()).select_from(Radicado).where(Radicado.numero.like(patron))
    )
    consecutivo = (existentes or 0) + 1
    return f"{fecha.year}-{prefijo}-{consecutivo}"


def crear_radicado(session: Session, datos: RadicadoCrear) -> Radicado:
    fecha = datos.fecha_radicacion or date.today()
    radicado = Radicado(
        numero=generar_numero(session, datos.tipo, fecha),
        tipo=datos.tipo.value,
        asunto=datos.asunto.strip(),
        descripcion=datos.descripcion,
        remitente=datos.remitente,
        fecha_radicacion=fecha,
        fecha_vencimiento=calcular_vencimiento(datos.tipo, fecha),
    )
    session.add(radicado)
    session.commit()
    session.refresh(radicado)
    return radicado


def buscar_radicados(session: Session, q: str | None = None) -> list[Radicado]:
    radicados = list(session.scalars(select(Radicado).order_by(Radicado.id.desc())))
    if not q:
        return radicados
    return [r for r in radicados if q in r.asunto or q in r.numero]


def obtener_por_numero(session: Session, numero: str) -> Radicado | None:
    return session.scalar(select(Radicado).where(Radicado.numero == numero))


def anular_radicado(session: Session, radicado: Radicado, motivo: str) -> Radicado:
    radicado.estado = EstadoRadicado.ANULADO.value
    radicado.motivo_anulacion = motivo.strip()
    radicado.fecha_anulacion = date.today()
    session.commit()
    session.refresh(radicado)
    return radicado
