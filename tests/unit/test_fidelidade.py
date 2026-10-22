import pytest

from BarberTime.domain.fidelidade import Fidelidade


def criar_fidelidade(**kwargs):
    dados = {
        "id": 1,
        "cliente_id": 100,
        "cortes_concluidos": 10,
        "possui_no_show": False,
        "cortes_para_gratis": 10,
    }
    dados.update(kwargs)
    return Fidelidade(**dados)


def test_cliente_pode_resgatar_com_meta_atingida_sem_no_show():
    fidelidade = criar_fidelidade()

    assert fidelidade.pode_resgatar_corte_gratis() is True


def test_cliente_nao_pode_resgatar_sem_cortes_suficientes():
    fidelidade = criar_fidelidade(cortes_concluidos=9)

    assert fidelidade.pode_resgatar_corte_gratis() is False


def test_cliente_com_no_show_nao_pode_resgatar():
    fidelidade = criar_fidelidade(possui_no_show=True)

    assert fidelidade.pode_resgatar_corte_gratis() is False


def test_registrar_corte_concluido_atualiza_progresso():
    fidelidade = criar_fidelidade(cortes_concluidos=4)

    fidelidade.registrar_corte_concluido()

    assert fidelidade.cortes_concluidos == 5
    assert fidelidade.cortes_restantes == 5


def test_registrar_no_show_bloqueia_resgate():
    fidelidade = criar_fidelidade()

    fidelidade.registrar_no_show()

    assert fidelidade.possui_no_show is True
    assert fidelidade.pode_resgatar_corte_gratis() is False


def test_resgate_rejeita_cliente_com_no_show():
    fidelidade = criar_fidelidade(possui_no_show=True)

    with pytest.raises(ValueError, match="no-show"):
        fidelidade.resgatar_corte_gratis()


def test_resgate_rejeita_cliente_sem_meta_atingida():
    fidelidade = criar_fidelidade(cortes_concluidos=5)

    with pytest.raises(ValueError, match="cortes suficientes"):
        fidelidade.resgatar_corte_gratis()


def test_resgate_consume_apenas_a_meta_de_cortes():
    fidelidade = criar_fidelidade(cortes_concluidos=12)

    fidelidade.resgatar_corte_gratis()

    assert fidelidade.cortes_concluidos == 2
    assert fidelidade.cortes_restantes == 8
    assert fidelidade.pode_resgatar_corte_gratis() is False


def test_meta_de_cortes_deve_ser_positiva():
    with pytest.raises(ValueError):
        criar_fidelidade(cortes_para_gratis=0)


def test_quantidade_de_cortes_nao_pode_ser_negativa():
    with pytest.raises(ValueError):
        criar_fidelidade(cortes_concluidos=-1)
