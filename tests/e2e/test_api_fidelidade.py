
def test_api_cadastrar_fidelidade(client):
    response = client.post(
        "/fidelidades",
        json={
            "id": 1,
            "cliente_id": 100,
            "cortes_para_gratis": 10
        }
    )

    assert response.status_code == 201
    assert response.get_json()["cliente_id"] == 100


def test_api_registrar_corte(client):
    client.post(
        "/fidelidades",
        json={"id": 1, "cliente_id": 100}
    )

    response = client.post("/fidelidades/1/cortes")

    assert response.status_code == 200
    assert response.get_json()["cortes_concluidos"] == 1


def test_api_bloquear_resgate_com_no_show(client):
    client.post(
        "/fidelidades",
        json={
            "id": 1,
            "cliente_id": 100,
            "cortes_para_gratis": 10
        }
    )

    for _ in range(10):
        client.post("/fidelidades/1/cortes")

    client.post("/fidelidades/1/no-show")

    response = client.post("/fidelidades/1/resgatar")

    assert response.status_code == 400
    assert "no-show" in response.get_json()["erro"]


def test_api_resgatar_corte_gratis(client):
    client.post(
        "/fidelidades",
        json={
            "id": 1,
            "cliente_id": 100,
            "cortes_para_gratis": 10
        }
    )

    for _ in range(10):
        client.post("/fidelidades/1/cortes")

    response = client.post("/fidelidades/1/resgatar")

    assert response.status_code == 200
    assert response.get_json()["cortes_concluidos"] == 0


def test_api_consultar_fidelidade_inexistente(client):
    response = client.get("/fidelidades/999")

    assert response.status_code == 404
