import re


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


def test_formato_numero_radicado_con_ceros_a_la_izquierda(client):
    r1 = _radicar(client, fecha_radicacion="2026-03-02", tipo="PETICION")
    assert r1.status_code == 201
    numero1 = r1.json()["numero"]
    assert numero1 == "2026-P-000001"
    assert re.match(r"^\d{4}-[PQRSDCI]-\d{6}$", numero1)

    r2 = _radicar(client, fecha_radicacion="2026-03-02", tipo="PETICION")
    assert r2.status_code == 201
    numero2 = r2.json()["numero"]
    assert numero2 == "2026-P-000002"

    r_queja = _radicar(client, fecha_radicacion="2026-03-02", tipo="QUEJA")
    assert r_queja.status_code == 201
    numero_queja = r_queja.json()["numero"]
    assert numero_queja == "2026-Q-000001"

    r_otro_ano = _radicar(client, fecha_radicacion="2027-01-15", tipo="PETICION")
    assert r_otro_ano.status_code == 201
    numero_otro_ano = r_otro_ano.json()["numero"]
    assert numero_otro_ano == "2027-P-000001"
