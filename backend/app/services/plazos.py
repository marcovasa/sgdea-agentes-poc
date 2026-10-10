"""Cálculo de plazos de respuesta de PQRSDF (Ley 1755 de 2015)."""

from datetime import date, timedelta

from app.models import TipoPQRSDF

# Días de respuesta por tipo de solicitud.
DIAS_RESPUESTA: dict[TipoPQRSDF, int] = {
    TipoPQRSDF.PETICION: 15,
    TipoPQRSDF.QUEJA: 15,
    TipoPQRSDF.RECLAMO: 15,
    TipoPQRSDF.SUGERENCIA: 15,
    TipoPQRSDF.DENUNCIA: 15,
    TipoPQRSDF.CONSULTA: 30,
    TipoPQRSDF.INFORMACION: 10,
}


def calcular_vencimiento(tipo: TipoPQRSDF, fecha_radicacion: date) -> date:
    """Devuelve la fecha límite de respuesta para un radicado."""
    dias = DIAS_RESPUESTA[tipo]
    return fecha_radicacion + timedelta(days=dias)
