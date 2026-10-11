from datetime import date

from sqlalchemy import select

from app.db import SessionLocal
from app.models import EstadoRadicado, Radicado


def _radicar(client, **extra):
    datos = {
        "tipo": "PETICION",
        "asunto": "Solicitud de certificado laboral",
        "remitente": "Ana Gómez",
        "fecha_radicacion": "2026-03-02",
    }
    datos.update(extra)
    return client.post("/api/radicados", json=datos)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_radicar_crea_radicado(client):
    r = _radicar(client)
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["numero"].startswith("2026-P-")
    assert cuerpo["estado"] == "RADICADO"
    assert cuerpo["tipo"] == "PETICION"


def test_consecutivo_aumenta_por_tipo(client):
    a = _radicar(client).json()["numero"]
    b = _radicar(client).json()["numero"]
    c = _radicar(client, tipo="QUEJA").json()["numero"]
    assert a != b
    assert c.startswith("2026-Q-")


def test_obtener_por_numero(client):
    numero = _radicar(client).json()["numero"]
    r = client.get(f"/api/radicados/{numero}")
    assert r.status_code == 200
    assert r.json()["numero"] == numero


def test_obtener_inexistente_404(client):
    assert client.get("/api/radicados/2026-P-999999").status_code == 404


def test_listar_y_buscar(client):
    _radicar(client, asunto="Derecho de petición sobre contrato")
    _radicar(client, asunto="Queja por atención")
    todos = client.get("/api/radicados").json()
    assert todos["total"] == 2
    filtrados = client.get("/api/radicados", params={"q": "contrato"}).json()
    assert filtrados["total"] == 1


def test_asunto_muy_corto_422(client):
    assert _radicar(client, asunto="ab").status_code == 422


def test_anular_radicado_exitoso(client):
    numero = _radicar(client).json()["numero"]
    motivo = "Documento duplicado por error del usuario"
    r = client.post(f"/api/radicados/{numero}/anular", json={"motivo": motivo})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["estado"] == "ANULADO"
    assert cuerpo["motivo_anulacion"] == motivo
    assert cuerpo["fecha_anulacion"] == date.today().isoformat()


def test_anular_motivo_menor_a_10_caracteres_422(client):
    numero = _radicar(client).json()["numero"]
    r = client.post(f"/api/radicados/{numero}/anular", json={"motivo": "corto"})
    assert r.status_code == 422


def test_anular_sin_motivo_422(client):
    numero = _radicar(client).json()["numero"]
    r = client.post(f"/api/radicados/{numero}/anular", json={})
    assert r.status_code == 422


def test_anular_inexistente_404(client):
    r = client.post(
        "/api/radicados/2026-P-999999/anular",
        json={"motivo": "Motivo suficientemente largo"},
    )
    assert r.status_code == 404


def test_anular_ya_anulado_409(client):
    numero = _radicar(client).json()["numero"]
    r1 = client.post(
        f"/api/radicados/{numero}/anular",
        json={"motivo": "Motivo suficientemente largo"},
    )
    assert r1.status_code == 200
    r2 = client.post(
        f"/api/radicados/{numero}/anular",
        json={"motivo": "Otro motivo suficientemente largo"},
    )
    assert r2.status_code == 409


def test_anular_respondido_409(client):
    numero = _radicar(client).json()["numero"]
    with SessionLocal() as session:
        radicado = session.scalar(select(Radicado).where(Radicado.numero == numero))
        radicado.estado = EstadoRadicado.RESPONDIDO
        session.commit()

    r = client.post(
        f"/api/radicados/{numero}/anular",
        json={"motivo": "Motivo suficientemente largo"},
    )
    assert r.status_code == 409


def test_radicado_anulado_aparece_en_listado(client):
    numero = _radicar(client).json()["numero"]
    client.post(
        f"/api/radicados/{numero}/anular",
        json={"motivo": "Motivo suficientemente largo"},
    )
    r = client.get("/api/radicados")
    assert r.status_code == 200
    items = r.json()["items"]
    encontrado = next(item for item in items if item["numero"] == numero)
    assert encontrado["estado"] == "ANULADO"
    assert encontrado["motivo_anulacion"] == "Motivo suficientemente largo"
