from datetime import date

from app.models import TipoPQRSDF
from app.services.plazos import (
    DIAS_RESPUESTA,
    FESTIVOS_COLOMBIA_2026,
    calcular_vencimiento,
)


def test_todos_los_tipos_tienen_plazo():
    assert set(DIAS_RESPUESTA) == set(TipoPQRSDF)


def test_festivos_colombia_2026():
    esperados = {
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
    assert FESTIVOS_COLOMBIA_2026 == esperados


def test_vencimiento_es_posterior_a_radicacion():
    inicio = date(2026, 3, 2)
    for tipo in TipoPQRSDF:
        assert calcular_vencimiento(tipo, inicio) > inicio


def test_consulta_tiene_mas_plazo_que_informacion():
    inicio = date(2026, 3, 2)
    assert calcular_vencimiento(TipoPQRSDF.CONSULTA, inicio) > calcular_vencimiento(
        TipoPQRSDF.INFORMACION, inicio
    )


def test_vencimiento_peticion_con_festivo():
    inicio = date(2026, 3, 2)
    vencimiento = calcular_vencimiento(TipoPQRSDF.PETICION, inicio)
    assert vencimiento == date(2026, 3, 24)


def test_vencimiento_informacion_semana_santa():
    inicio = date(2026, 3, 27)
    vencimiento = calcular_vencimiento(TipoPQRSDF.INFORMACION, inicio)
    assert vencimiento == date(2026, 4, 14)


def test_vencimiento_consulta_treinta_dias():
    inicio = date(2026, 6, 1)
    vencimiento = calcular_vencimiento(TipoPQRSDF.CONSULTA, inicio)
    assert vencimiento == date(2026, 7, 16)
