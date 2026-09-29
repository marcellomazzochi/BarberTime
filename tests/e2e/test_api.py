import pytest

def test_api_criar_barbeiro(client):
    response = client.post(
        "/barbeiros",
        json={
            "id": 1,
            "nome": "Jonathan Melo",
            "horario_inicio": "08:00",
            "horario_fim": "18:00",
            "dias_trabalho": "0,1,2,3,4,5",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 1
    assert data["nome"] == "Jonathan Melo"
    assert data["horario_inicio"] == "08:00"

def test_api_criar_barbeiro_duplicado_retorna_400(client):
    client.post("/barbeiros", json={"id": 1, "nome": "Jonathan"})
    response = client.post("/barbeiros", json={"id": 1, "nome": "Outro Barbeiro"})
    assert response.status_code == 400
    assert "ja cadastrado" in response.get_json()["erro"]

def test_api_listar_barbeiros(client):
    client.post("/barbeiros", json={"id": 1, "nome": "Jonathan"})
    client.post("/barbeiros", json={"id": 2, "nome": "Carlos"})
    response = client.get("/barbeiros")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2

def test_api_obter_barbeiro(client):
    client.post("/barbeiros", json={"id": 1, "nome": "Jonathan"})
    response = client.get("/barbeiros/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1
    assert data["nome"] == "Jonathan"

def test_api_obter_barbeiro_inexistente(client):
    response = client.get("/barbeiros/999")
    assert response.status_code == 404
    assert "nao encontrado" in response.get_json()["erro"]

def test_api_atualizar_expediente(client):
    client.post("/barbeiros", json={"id": 1, "nome": "Jonathan", "horario_inicio": "08:00", "horario_fim": "18:00"})
    response = client.put(
        "/barbeiros/1/expediente",
        json={"horario_inicio": "09:00", "horario_fim": "17:00"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["horario_inicio"] == "09:00"
    assert data["horario_fim"] == "17:00"

def test_api_validar_horario_disponivel(client):
    client.post(
        "/barbeiros",
        json={"id": 1, "nome": "Jonathan", "horario_inicio": "08:00", "horario_fim": "18:00", "dias_trabalho": "0,1,2,3,4,5"},
    )
    response = client.post(
        "/barbeiros/1/validar_horario",
        json={"data_hora": "2026-10-05T10:00:00", "duracao": 30},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["valido"] is True

def test_api_validar_horario_fora_do_expediente(client):
    client.post(
        "/barbeiros",
        json={"id": 1, "nome": "Jonathan", "horario_inicio": "08:00", "horario_fim": "18:00"},
    )
    # Horario as 07:00 da manha (antes do expediente)
    response = client.post(
        "/barbeiros/1/validar_horario",
        json={"data_hora": "2026-10-05T07:00:00", "duracao": 30},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["valido"] is False
    assert "antes do inicio do expediente" in data["erro"]
