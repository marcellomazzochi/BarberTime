import pytest


def criar_barbeiro_e_atendimento(client):
    client.post("/barbeiros", json={"id": 1, "nome": "Ruan"})
    return client.post(
        "/atendimentos",
        json={
            "id": 1,
            "barbeiro_id": 1,
            "servico": {"nome": "Corte", "duracao": 30, "preco": 50.0},
            "data_hora": "2026-10-05T10:00:00",
        },
    )


def test_api_registrar_atendimento(client):
    response = criar_barbeiro_e_atendimento(client)
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 1
    assert data["barbeiro_id"] == 1
    assert data["servico"]["preco"] == 50.0
    assert data["status"] == "Agendado"


def test_api_registrar_atendimento_barbeiro_inexistente(client):
    response = client.post(
        "/atendimentos",
        json={
            "id": 1,
            "barbeiro_id": 999,
            "servico": {"nome": "Corte", "duracao": 30, "preco": 50.0},
            "data_hora": "2026-10-05T10:00:00",
        },
    )
    assert response.status_code == 400
    assert "nao encontrado" in response.get_json()["erro"]


def test_api_nao_gera_comissao_para_atendimento_nao_concluido(client):
    criar_barbeiro_e_atendimento(client)
    response = client.post("/comissoes", json={"id": 1, "atendimento_id": 1})
    assert response.status_code == 400
    assert "nao concluido" in response.get_json()["erro"]


def test_api_concluir_atendimento_e_gerar_comissao(client):
    criar_barbeiro_e_atendimento(client)

    concluido = client.post("/atendimentos/1/concluir")
    assert concluido.status_code == 200
    assert concluido.get_json()["status"] == "Concluido"

    response = client.post("/comissoes", json={"id": 1, "atendimento_id": 1})
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 1
    assert data["barbeiro_id"] == 1
    assert data["atendimento_id"] == 1
    assert data["percentual"] == 10.0
    assert data["valor"] == 5.0


def test_api_gerar_comissao_com_percentual_customizado(client):
    criar_barbeiro_e_atendimento(client)
    client.post("/atendimentos/1/concluir")

    response = client.post("/comissoes", json={"id": 1, "atendimento_id": 1, "percentual": 30})
    assert response.status_code == 201
    data = response.get_json()
    assert data["percentual"] == 30.0
    assert data["valor"] == 15.0


def test_api_nao_gera_comissao_duplicada(client):
    criar_barbeiro_e_atendimento(client)
    client.post("/atendimentos/1/concluir")
    client.post("/comissoes", json={"id": 1, "atendimento_id": 1})

    response = client.post("/comissoes", json={"id": 2, "atendimento_id": 1})
    assert response.status_code == 400
    assert "Ja existe comissao" in response.get_json()["erro"]


def test_api_listar_e_consultar_comissoes(client):
    criar_barbeiro_e_atendimento(client)
    client.post("/atendimentos/1/concluir")
    client.post("/comissoes", json={"id": 1, "atendimento_id": 1})

    listagem = client.get("/comissoes")
    assert listagem.status_code == 200
    assert len(listagem.get_json()) == 1

    consulta = client.get("/comissoes/1")
    assert consulta.status_code == 200
    assert consulta.get_json()["valor"] == 5.0

    do_barbeiro = client.get("/barbeiros/1/comissoes")
    assert do_barbeiro.status_code == 200
    assert len(do_barbeiro.get_json()) == 1


def test_api_consultar_comissao_inexistente(client):
    response = client.get("/comissoes/999")
    assert response.status_code == 404
