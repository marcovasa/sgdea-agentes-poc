from datetime import date

from app.models import TipoPQRSDF
from app.services.plazos import DIAS_RESPUESTA, calcular_vencimiento


def test_todos_los_tipos_tienen_plazo():
    assert set(DIAS_RESPUESTA) == set(TipoPQRSDF)


def test_vencimiento_es_posterior_a_radicacion():
    inicio = date(2026, 3, 2)
    for tipo in TipoPQRSDF:
        assert calcular_vencimiento(tipo, inicio) > inicio


def test_consulta_tiene_mas_plazo_que_informacion():
    inicio = date(2026, 3, 2)
    assert calcular_vencimiento(TipoPQRSDF.CONSULTA, inicio) > calcular_vencimiento(
        TipoPQRSDF.INFORMACION, inicio
    )
