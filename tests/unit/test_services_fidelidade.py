
import pytest

from BarberTime.domain.model import Fidelidade
from BarberTime.adapters.repository import FakeFidelidadeRepository
from BarberTime.service_layer import services


@pytest.fixture
def repo():
    return FakeFidelidadeRepository()


def test_cadastrar_fidelidade(repo):
    resultado = services.cadastrar_fidelidade(
        id=1,
        cliente_id=100,
        fidelidade_repo=repo
    )

    assert resultado["cliente_id"] == 100
    assert resultado["cortes_concluidos"] == 0
    assert resultado["cortes_para_gratis"] == 10


def test_nao_cadastrar_fidelidade_duplicada(repo):
    services.cadastrar_fidelidade(1, 100, repo)

    with pytest.raises(ValueError):
        services.cadastrar_fidelidade(2, 100, repo)


def test_consultar_fidelidade(repo):
    services.cadastrar_fidelidade(1, 100, repo)

    resultado = services.consultar_fidelidade(1, repo)

    assert resultado["id"] == 1


def test_registrar_corte_fidelidade(repo):
    services.cadastrar_fidelidade(1, 100, repo)

    resultado = services.registrar_corte_fidelidade(1, repo)

    assert resultado["cortes_concluidos"] == 1


def test_registrar_no_show_fidelidade(repo):
    services.cadastrar_fidelidade(1, 100, repo)

    resultado = services.registrar_no_show_fidelidade(1, repo)

    assert resultado["possui_no_show"] is True
    assert resultado["pode_resgatar_corte_gratis"] is False


def test_resgatar_corte_gratis_com_sucesso(repo):
    fidelidade = Fidelidade(
        id=1,
        cliente_id=100,
        cortes_concluidos=10
    )
    repo.add(fidelidade)

    resultado = services.resgatar_corte_gratis(1, repo)

    assert resultado["cortes_concluidos"] == 0
    assert resultado["corte_gratis_disponivel"] is False


def test_bloquear_resgate_com_no_show(repo):
    fidelidade = Fidelidade(
        id=1,
        cliente_id=100,
        cortes_concluidos=10,
        possui_no_show=True
    )
    repo.add(fidelidade)

    with pytest.raises(ValueError, match="no-show"):
        services.resgatar_corte_gratis(1, repo)


def test_bloquear_resgate_sem_meta(repo):
    fidelidade = Fidelidade(
        id=1,
        cliente_id=100,
        cortes_concluidos=5
    )
    repo.add(fidelidade)

    with pytest.raises(ValueError, match="cortes suficientes"):
        services.resgatar_corte_gratis(1, repo)


def test_consultar_fidelidade_inexistente(repo):
    with pytest.raises(ValueError):
        services.consultar_fidelidade(999, repo)


def test_listar_fidelidades(repo):
    services.cadastrar_fidelidade(1, 100, repo)
    services.cadastrar_fidelidade(2, 200, repo)

    resultado = services.listar_fidelidades(repo)

    assert len(resultado) == 2
