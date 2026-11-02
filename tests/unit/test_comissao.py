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
    # Estrategias OCP
    EstrategiaComissao,
    ComissaoPercentualFixo,
    ComissaoBarbeiroSenior,
    ComissaoBarbeiroJunior,
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


# ---------------------------------------------------------------------------
# Testes originais (comportamento preservado apos refatoracao)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Novos testes — OCP: Strategy de Comissao
# ---------------------------------------------------------------------------

def test_estrategia_percentual_fixo_e_subclasse_de_estrategia_comissao():
    """EstrategiaComissao e uma ABC; ComissaoPercentualFixo implementa o contrato."""
    estrategia = ComissaoPercentualFixo(20.0)
    assert isinstance(estrategia, EstrategiaComissao)


def test_estrategia_percentual_fixo_calcula_valor_correto():
    estrategia = ComissaoPercentualFixo(10.0)
    assert estrategia.calcular(50.0) == 5.0

    estrategia_30 = ComissaoPercentualFixo(30.0)
    assert estrategia_30.calcular(100.0) == 30.0


def test_estrategia_senior_calcula_15_porcento():
    """Barbeiro senior: 15% sem desconto."""
    estrategia = ComissaoBarbeiroSenior()
    # 15% de R$100 = R$15
    assert estrategia.calcular(100.0) == 15.0
    # 15% de R$50 = R$7.50
    assert estrategia.calcular(50.0) == 7.5


def test_estrategia_junior_calcula_10_porcento_menos_desconto_insumos():
    """Barbeiro junior: 10% - R$5 de insumos."""
    estrategia = ComissaoBarbeiroJunior()
    # 10% de R$50 = R$5 - R$5 desconto = R$0 (nao negativo)
    assert estrategia.calcular(50.0) == 0.0
    # 10% de R$100 = R$10 - R$5 = R$5
    assert estrategia.calcular(100.0) == 5.0
    # 10% de R$200 = R$20 - R$5 = R$15
    assert estrategia.calcular(200.0) == 15.0


def test_estrategia_junior_nao_retorna_valor_negativo():
    """Com servico muito barato, comissao junior nao pode ser negativa."""
    estrategia = ComissaoBarbeiroJunior()
    # 10% de R$10 = R$1 - R$5 = -R$4 => deve ser R$0
    assert estrategia.calcular(10.0) == 0.0


def test_comissao_com_estrategia_senior_calcula_15_porcento():
    """Usando estrategia senior diretamente no construtor de Comissao."""
    atendimento = criar_atendimento()
    atendimento.concluir()

    comissao = Comissao(id=1, atendimento=atendimento, estrategia=ComissaoBarbeiroSenior())
    # 15% de R$50 = R$7.50
    assert comissao.valor == 7.5
    # Sem percentual unico definido (strategy nao e PercentualFixo)
    assert comissao.percentual is None


def test_comissao_com_estrategia_junior_aplica_desconto_de_insumos():
    """Usando estrategia junior diretamente no construtor de Comissao."""
    atendimento = criar_atendimento()
    atendimento.concluir()

    comissao = Comissao(id=1, atendimento=atendimento, estrategia=ComissaoBarbeiroJunior())
    # 10% de R$50 = R$5 - R$5 = R$0
    assert comissao.valor == 0.0
    assert comissao.percentual is None


def test_comissao_com_estrategia_percentual_fixo_expoe_percentual():
    """Estrategia PercentualFixo expoe o percentual para retrocompatibilidade."""
    atendimento = criar_atendimento()
    atendimento.concluir()

    estrategia = ComissaoPercentualFixo(20.0)
    comissao = Comissao(id=1, atendimento=atendimento, estrategia=estrategia)
    assert comissao.percentual.valor == 20.0
    assert comissao.valor == 10.0  # 20% de R$50


def test_comissao_estrategia_e_legado_percentual_sao_equivalentes_para_padrao():
    """Instanciar Comissao sem args (10%) deve dar mesmo valor que estrategia padrao explicita."""
    atendimento = criar_atendimento()
    atendimento.concluir()

    c_legado = Comissao(id=1, atendimento=atendimento)
    c_estrategia = Comissao(id=2, atendimento=atendimento, estrategia=ComissaoPercentualFixo(10.0))

    assert c_legado.valor == c_estrategia.valor == 5.0


def test_estrategia_e_abc_nao_pode_ser_instanciada_diretamente():
    """EstrategiaComissao e abstrata; instanciar diretamente deve lancar TypeError."""
    with pytest.raises(TypeError):
        EstrategiaComissao()


def test_nova_estrategia_sem_modificar_comissao(monkeypatch):
    """OCP: e possivel adicionar nova politica de comissao sem alterar Comissao."""

    class ComissaoFidelidade(EstrategiaComissao):
        """Estrategia hipotetica: desconto de 20% para clientes fidelizados."""
        def calcular(self, preco_servico: float) -> float:
            return round(preco_servico * 0.20, 2)

    atendimento = criar_atendimento()
    atendimento.concluir()

    comissao = Comissao(id=1, atendimento=atendimento, estrategia=ComissaoFidelidade())
    # 20% de R$50 = R$10
    assert comissao.valor == 10.0
