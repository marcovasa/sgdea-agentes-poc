"""Cálculo de plazos de respuesta de PQRSDF (Ley 1755 de 2015)."""

from datetime import date, timedelta

from app.models import TipoPQRSDF

# Días de respuesta por tipo de solicitud (días hábiles).
DIAS_RESPUESTA: dict[TipoPQRSDF, int] = {
    TipoPQRSDF.PETICION: 15,
    TipoPQRSDF.QUEJA: 15,
    TipoPQRSDF.RECLAMO: 15,
    TipoPQRSDF.SUGERENCIA: 15,
    TipoPQRSDF.DENUNCIA: 15,
    TipoPQRSDF.CONSULTA: 30,
    TipoPQRSDF.INFORMACION: 10,
}

# Festivos oficiales de Colombia para 2026.
FESTIVOS_COLOMBIA_2026: frozenset[date] = frozenset(
    {
        date(2026, 1, 1),
        date(2026, 1, 12),
        date(2026, 3, 23),
        date(2026, 4, 2),
        date(2026, 4, 3),
        date(2026, 5, 1),
        date(2026, 5, 18),
        date(2026, 6, 8),
        date(2026, 6, 15),
        date(2026, 6, 29),
        date(2026, 7, 20),
        date(2026, 8, 7),
        date(2026, 8, 17),
        date(2026, 10, 12),
        date(2026, 11, 2),
        date(2026, 11, 16),
        date(2026, 12, 8),
        date(2026, 12, 25),
    }
)


def es_dia_habil(dia: date) -> bool:
    """Indica si una fecha corresponde a un día hábil (lunes a viernes no festivo)."""
    return dia.weekday() < 5 and dia not in FESTIVOS_COLOMBIA_2026


def calcular_vencimiento(tipo: TipoPQRSDF, fecha_radicacion: date) -> date:
    """Devuelve la fecha límite de respuesta para un radicado en días hábiles."""
    dias_restantes = DIAS_RESPUESTA[tipo]
    actual = fecha_radicacion
    while dias_restantes > 0:
        actual += timedelta(days=1)
        if es_dia_habil(actual):
            dias_restantes -= 1
    return actual
