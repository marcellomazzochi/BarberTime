import pytest
from datetime import datetime

from BarberTime.domain.model import servico, StatusAtendimento
from BarberTime.adapters.repository import (
    FakeBarbeiroRepository,
    FakeAtendimentoRepository,
    FakeComissaoRepository,
)
from BarberTime.service_layer import services


def preparar_repos():
    barbeiros = FakeBarbeiroRepository()
    atendimentos = FakeAtendimentoRepository()
    comissoes = FakeComissaoRepository()
    services.cadastrar_barbeiro(id=1, nome="Ruan", repo=barbeiros)
    return barbeiros, atendimentos, comissoes


def test_service_registrar_atendimento():
    barbeiros, atendimentos, _ = preparar_repos()
    resultado = services.registrar_atendimento(
        atendimento_id=1,
        barbeiro_id=1,
        servico=servico(id=1, nome="Corte", duracao=30, preco=50.0),
        data_hora=datetime(2026, 10, 5, 10, 0),
        atendimento_repo=atendimentos,
        barbeiro_repo=barbeiros,
    )
    assert resultado["id"] == 1
    assert resultado["barbeiro_id"] == 1
    assert resultado["status"] == StatusAtendimento.AGENDADO.value
    assert resultado["servico"]["preco"] == 50.0
    assert atendimentos.get(1) is not None


def test_service_registrar_atendimento_duplicado_rejeita():
    barbeiros, atendimentos, _ = preparar_repos()
    services.registrar_atendimento(1, 1, servico(1, "Corte", 30, 50.0), datetime(2026, 10, 5, 10, 0), atendimentos, barbeiros)
    with pytest.raises(ValueError, match="ja cadastrado"):
        services.registrar_atendimento(1, 1, servico(1, "Corte", 30, 50.0), datetime(2026, 10, 5, 11, 0), atendimentos, barbeiros)


def test_service_registrar_atendimento_barbeiro_inexistente():
    _, atendimentos, _ = preparar_repos()
    barbeiros = FakeBarbeiroRepository()
    with pytest.raises(ValueError, match="Barbeiro com id 999 nao encontrado"):
        services.registrar_atendimento(1, 999, servico(1, "Corte", 30, 50.0), datetime(2026, 10, 5, 10, 0), atendimentos, barbeiros)


def test_service_nao_gera_comissao_para_atendimento_nao_concluido():
    barbeiros, atendimentos, comissoes = preparar_repos()
    services.registrar_atendimento(1, 1, servico(1, "Corte", 30, 50.0), datetime(2026, 10, 5, 10, 0), atendimentos, barbeiros)

    with pytest.raises(ValueError, match="nao concluido"):
        services.gerar_comissao(1, 1, atendimentos, comissoes)


def test_service_concluir_atendimento_e_gerar_comissao():
    barbeiros, atendimentos, comissoes = preparar_repos()
    services.registrar_atendimento(1, 1, servico(1, "Corte", 30, 50.0), datetime(2026, 10, 5, 10, 0), atendimentos, barbeiros)

    concluido = services.concluir_atendimento(atendimento_id=1, atendimento_repo=atendimentos)
    assert concluido["status"] == StatusAtendimento.CONCLUIDO.value

    comissao = services.gerar_comissao(
        comissao_id=1, atendimento_id=1, atendimento_repo=atendimentos, comissao_repo=comissoes
    )
    assert comissao["id"] == 1
    assert comissao["barbeiro_id"] == 1
    assert comissao["atendimento_id"] == 1
    assert comissao["percentual"] == 10.0
    assert comissao["valor"] == 5.0


def test_service_gerar_comissao_percentual_customizado():
    barbeiros, atendimentos, comissoes = preparar_repos()
    services.registrar_atendimento(1, 1, servico(1, "Corte", 30, 50.0), datetime(2026, 10, 5, 10, 0), atendimentos, barbeiros)
    services.concluir_atendimento(1, atendimentos)

    comissao = services.gerar_comissao(1, 1, atendimentos, comissoes, percentual=20.0)
    assert comissao["percentual"] == 20.0
    assert comissao["valor"] == 10.0


def test_service_nao_gera_comissao_duplicada_para_mesmo_atendimento():
    barbeiros, atendimentos, comissoes = preparar_repos()
    services.registrar_atendimento(1, 1, servico(1, "Corte", 30, 50.0), datetime(2026, 10, 5, 10, 0), atendimentos, barbeiros)
    services.concluir_atendimento(1, atendimentos)
    services.gerar_comissao(1, 1, atendimentos, comissoes)

    with pytest.raises(ValueError, match="Ja existe comissao"):
        services.gerar_comissao(2, 1, atendimentos, comissoes)


def test_service_gerar_comissao_com_id_duplicado_rejeita():
    barbeiros, atendimentos, comissoes = preparar_repos()
    services.registrar_atendimento(1, 1, servico(1, "Corte", 30, 50.0), datetime(2026, 10, 5, 10, 0), atendimentos, barbeiros)
    services.registrar_atendimento(2, 1, servico(1, "Corte", 30, 50.0), datetime(2026, 10, 5, 11, 0), atendimentos, barbeiros)
    services.concluir_atendimento(1, atendimentos)
    services.concluir_atendimento(2, atendimentos)
    services.gerar_comissao(1, 1, atendimentos, comissoes)

    with pytest.raises(ValueError, match="ja cadastrada"):
        services.gerar_comissao(1, 2, atendimentos, comissoes)


def test_service_gerar_comissao_atendimento_inexistente():
    _, atendimentos, comissoes = preparar_repos()
    with pytest.raises(ValueError, match="Atendimento com id 99 nao encontrado"):
        services.gerar_comissao(1, 99, atendimentos, comissoes)


def test_service_consultar_comissao():
    barbeiros, atendimentos, comissoes = preparar_repos()
    services.registrar_atendimento(1, 1, servico(1, "Corte", 30, 50.0), datetime(2026, 10, 5, 10, 0), atendimentos, barbeiros)
    services.concluir_atendimento(1, atendimentos)
    services.gerar_comissao(1, 1, atendimentos, comissoes)

    consultada = services.consultar_comissao(comissao_id=1, repo=comissoes)
    assert consultada["id"] == 1
    assert consultada["valor"] == 5.0


def test_service_consultar_comissao_inexistente():
    _, _, comissoes = preparar_repos()
    with pytest.raises(ValueError, match="nao encontrada"):
        services.consultar_comissao(comissao_id=999, repo=comissoes)


def test_service_listar_comissoes_por_barbeiro():
    barbeiros, atendimentos, comissoes = preparar_repos()
    services.cadastrar_barbeiro(id=2, nome="Outro", repo=barbeiros)
    services.registrar_atendimento(1, 1, servico(1, "Corte", 30, 50.0), datetime(2026, 10, 5, 10, 0), atendimentos, barbeiros)
    services.registrar_atendimento(2, 2, servico(1, "Corte", 30, 80.0), datetime(2026, 10, 5, 11, 0), atendimentos, barbeiros)
    services.concluir_atendimento(1, atendimentos)
    services.concluir_atendimento(2, atendimentos)
    services.gerar_comissao(1, 1, atendimentos, comissoes)
    services.gerar_comissao(2, 2, atendimentos, comissoes)

    do_barbeiro_1 = services.listar_comissoes_por_barbeiro(barbeiro_id=1, repo=comissoes)
    assert len(do_barbeiro_1) == 1
    assert do_barbeiro_1[0]["barbeiro_id"] == 1
    assert do_barbeiro_1[0]["valor"] == 5.0

    assert len(services.listar_comissoes(comissoes)) == 2
