import pytest
from datetime import datetime

from BarberTime.domain.model import (
    barbeiro,
    servico,
    Atendimento,
    Comissao,
    PercentualComissao,
    ServicoRealizado,
    StatusAtendimento,
)


def criar_atendimento(status=StatusAtendimento.AGENDADO, barbeiro_id=1):
    b = barbeiro(id=barbeiro_id, nome="Ruan")
    s = servico(id=1, nome="Corte", duracao=30, preco=50.0)
    return Atendimento(
        id=1,
        barbeiro=b,
        servico=s,
        data_hora=datetime(2026, 10, 5, 10, 0),
        status=status,
    )


def test_nao_gera_comissao_para_atendimento_agendado():
    atendimento = criar_atendimento(StatusAtendimento.AGENDADO)
    assert atendimento.concluido is False
    assert atendimento.pode_gerar_comissao() is False
    with pytest.raises(ValueError, match="nao concluido"):
        Comissao(id=1, atendimento=atendimento)


def test_nao_gera_comissao_para_atendimento_cancelado():
    atendimento = criar_atendimento(StatusAtendimento.CANCELADO)
    with pytest.raises(ValueError, match="nao concluido"):
        Comissao(id=1, atendimento=atendimento)


def test_nao_gera_comissao_para_atendimento_com_falta():
    atendimento = criar_atendimento(StatusAtendimento.FALTOU)
    with pytest.raises(ValueError, match="nao concluido"):
        Comissao(id=1, atendimento=atendimento)


def test_gera_comissao_para_atendimento_concluido():
    atendimento = criar_atendimento()
    atendimento.concluir()
    assert atendimento.concluido is True
    assert atendimento.pode_gerar_comissao() is True

    comissao = Comissao(id=1, atendimento=atendimento)
    assert comissao.id == 1
    assert comissao.atendimento == atendimento
    assert comissao.barbeiro == atendimento.barbeiro
    assert comissao.percentual.valor == 10.0
    assert comissao.valor == 5.0


def test_gera_comissao_com_percentual_customizado():
    atendimento = criar_atendimento()
    atendimento.concluir()

    comissao = Comissao(id=1, atendimento=atendimento, percentual=30.0)
    assert isinstance(comissao.percentual, PercentualComissao)
    assert comissao.percentual.valor == 30.0
    assert comissao.valor == 15.0


def test_gera_comissao_com_value_object_de_percentual():
    atendimento = criar_atendimento()
    atendimento.concluir()

    comissao = Comissao(id=1, atendimento=atendimento, percentual=PercentualComissao(25.0))
    assert comissao.valor == 12.5


def test_percentual_de_comissao_valida_intervalo():
    for invalido in [0, -1, 101, 150]:
        with pytest.raises(ValueError, match="Percentual de comissao"):
            PercentualComissao(invalido)

    assert PercentualComissao(0.5).valor == 0.5
    assert PercentualComissao(100).valor == 100


def test_nao_gera_comissao_de_atendimento_de_outro_barbeiro():
    atendimento = criar_atendimento()
    atendimento.concluir()
    outro_barbeiro = barbeiro(id=2, nome="Outro Barbeiro")

    with pytest.raises(ValueError, match="nao pertence ao barbeiro"):
        Comissao(id=1, atendimento=atendimento, barbeiro=outro_barbeiro)


def test_nao_gera_comissao_sem_atendimento():
    with pytest.raises(ValueError, match="obrigatorio"):
        Comissao(id=1, atendimento=None)


def test_concluir_atendimento_altera_status():
    atendimento = criar_atendimento()
    assert atendimento.status == StatusAtendimento.AGENDADO
    atendimento.concluir()
    assert atendimento.status == StatusAtendimento.CONCLUIDO


def test_cancelar_atendimento_concluido_rejeita():
    atendimento = criar_atendimento()
    atendimento.concluir()
    with pytest.raises(ValueError, match="ja concluido"):
        atendimento.cancelar()


def test_concluir_atendimento_cancelado_rejeita():
    atendimento = criar_atendimento()
    atendimento.cancelar()
    with pytest.raises(ValueError, match="cancelado"):
        atendimento.concluir()


def test_marcar_falta_em_atendimento_concluido_rejeita():
    atendimento = criar_atendimento()
    atendimento.concluir()
    with pytest.raises(ValueError, match="ja concluido"):
        atendimento.marcar_falta()


def test_atendimento_normaliza_data_hora_string_e_servico():
    b = barbeiro(id=1, nome="Ruan")
    s = servico(id=1, nome="Barba", duracao=20, preco=30.0)
    atendimento = Atendimento(
        id=7, barbeiro=b, servico=s, data_hora="2026-10-05T10:00:00"
    )

    assert atendimento.data_hora == datetime(2026, 10, 5, 10, 0)
    assert isinstance(atendimento.servico, ServicoRealizado)
    assert atendimento.servico.nome == "Barba"
    assert atendimento.servico.duracao == 20
    assert atendimento.servico.preco == 30.0


def test_atendimento_igualdade_por_identidade():
    a1 = criar_atendimento()
    a2 = criar_atendimento()
    a2.data_hora = datetime(2026, 10, 5, 15, 0)
    a3 = Atendimento(
        id=2,
        barbeiro=barbeiro(id=1, nome="Ruan"),
        servico=servico(id=1, nome="Corte", duracao=30, preco=50.0),
        data_hora=datetime(2026, 10, 5, 10, 0),
    )
    assert a1 == a2
    assert a1 != a3
    assert hash(a1) == hash(a2)


def test_comissao_igualdade_por_identidade():
    atendimento = criar_atendimento()
    atendimento.concluir()

    c1 = Comissao(id=1, atendimento=atendimento)
    c2 = Comissao(id=1, atendimento=atendimento)
    c3 = Comissao(id=2, atendimento=atendimento)

    assert c1 == c2
    assert c1 != c3
    assert hash(c1) == hash(c2)
