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


def test_radicar_sin_remitente_422(client):
    datos = {
        "tipo": "PETICION",
        "asunto": "Solicitud sin remitente",
        "fecha_radicacion": "2026-03-02",
    }
    r = client.post("/api/radicados", json=datos)
    assert r.status_code == 422


def test_radicar_remitente_vacio_422(client):
    assert _radicar(client, remitente="").status_code == 422


def test_radicar_remitente_espacios_422(client):
    assert _radicar(client, remitente="   ").status_code == 422


def test_radicar_remitente_muy_corto_422(client):
    assert _radicar(client, remitente="ab").status_code == 422


def test_radicar_remitente_valido_201(client):
    r = _radicar(client, remitente="Ana")
    assert r.status_code == 201
    assert r.json()["remitente"] == "Ana"


def test_listar_radicado_antiguo_sin_remitente(client):
    from datetime import date

    from app.db import SessionLocal
    from app.models import Radicado

    with SessionLocal() as session:
        radicado_antiguo = Radicado(
            numero="2025-P-1",
            tipo="PETICION",
            asunto="Petición antigua sin remitente",
            descripcion="",
            remitente=None,
            fecha_radicacion=date(2025, 1, 1),
            fecha_vencimiento=date(2025, 1, 20),
        )
        session.add(radicado_antiguo)
        session.commit()

    r = client.get("/api/radicados")
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 1
    assert cuerpo["items"][0]["remitente"] is None
