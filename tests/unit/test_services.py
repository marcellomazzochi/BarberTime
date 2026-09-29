import pytest
from datetime import datetime
from BarberTime.adapters.repository import FakeBarbeiroRepository
from BarberTime.service_layer import services

def test_service_cadastrar_barbeiro():
    repo = FakeBarbeiroRepository()
    resultado = services.cadastrar_barbeiro(
        id=1,
        nome="Jonathan",
        horario_inicio="08:00",
        horario_fim="18:00",
        repo=repo,
    )
    assert resultado["id"] == 1
    assert resultado["nome"] == "Jonathan"
    assert repo.get(1) is not None

def test_service_cadastrar_barbeiro_duplicado_rejeita():
    repo = FakeBarbeiroRepository()
    services.cadastrar_barbeiro(id=1, nome="Jonathan", repo=repo)
    with pytest.raises(ValueError, match="ja cadastrado"):
        services.cadastrar_barbeiro(id=1, nome="Jonathan Melo", repo=repo)

def test_service_consultar_barbeiro():
    repo = FakeBarbeiroRepository()
    services.cadastrar_barbeiro(id=1, nome="Jonathan", repo=repo)
    consultado = services.consultar_barbeiro(barbeiro_id=1, repo=repo)
    assert consultado["id"] == 1
    assert consultado["nome"] == "Jonathan"

def test_service_consultar_barbeiro_inexistente():
    repo = FakeBarbeiroRepository()
    with pytest.raises(ValueError, match="nao encontrado"):
        services.consultar_barbeiro(barbeiro_id=999, repo=repo)

def test_service_atualizar_expediente():
    repo = FakeBarbeiroRepository()
    services.cadastrar_barbeiro(id=1, nome="Jonathan", horario_inicio="08:00", horario_fim="18:00", repo=repo)
    atualizado = services.atualizar_expediente(
        barbeiro_id=1,
        novo_inicio="09:00",
        novo_fim="17:00",
        repo=repo,
    )
    assert atualizado["horario_inicio"] == "09:00"
    assert atualizado["horario_fim"] == "17:00"

def test_service_validar_horario_atendimento():
    repo = FakeBarbeiroRepository()
    services.cadastrar_barbeiro(id=1, nome="Jonathan", horario_inicio="08:00", horario_fim="18:00", repo=repo)
    # Segunda-feira valida
    dt_valida = datetime(2026, 10, 5, 11, 0)
    resultado = services.validar_horario_atendimento(barbeiro_id=1, data_hora=dt_valida, duracao_minutos=30, repo=repo)
    assert resultado["valido"] is True

    # Horario fora do expediente deve lancar ValueError
    dt_invalida = datetime(2026, 10, 5, 19, 0)
    with pytest.raises(ValueError, match="apos o encerramento do expediente"):
        services.validar_horario_atendimento(barbeiro_id=1, data_hora=dt_invalida, duracao_minutos=30, repo=repo)
