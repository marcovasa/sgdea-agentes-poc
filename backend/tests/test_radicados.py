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


def test_buscar_insensible_mayusculas_y_tildes(client):
    r = _radicar(client, asunto="Petición de copia de resolución")
    numero = r.json()["numero"]

    for termino in ["peticion", "PETICION", "Petición"]:
        res = client.get("/api/radicados", params={"q": termino}).json()
        assert res["total"] == 1, f"Falló buscando con '{termino}'"
        assert res["items"][0]["numero"] == numero


def test_buscar_por_numero_sigue_funcionando(client):
    r = _radicar(client, asunto="Solicitud de información general")
    numero = r.json()["numero"]

    res_exacto = client.get("/api/radicados", params={"q": numero}).json()
    assert res_exacto["total"] == 1
    assert res_exacto["items"][0]["numero"] == numero

    res_minusculas = client.get("/api/radicados", params={"q": numero.lower()}).json()
    assert res_minusculas["total"] == 1
    assert res_minusculas["items"][0]["numero"] == numero


def test_buscar_sin_coincidencias_devuelve_cero(client):
    _radicar(client, asunto="Derecho de petición sobre contrato")
    res = client.get("/api/radicados", params={"q": "inexistente"}).json()
    assert res["total"] == 0
    assert res["items"] == []
