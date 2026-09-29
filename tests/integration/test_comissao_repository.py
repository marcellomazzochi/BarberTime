import pytest
from datetime import datetime
from sqlalchemy import text

from BarberTime.domain.model import barbeiro, servico, Atendimento, Comissao, StatusAtendimento
from BarberTime.adapters.repository import (
    SqlAlchemyBarbeiroRepository,
    SqlAlchemyAtendimentoRepository,
    SqlAlchemyComissaoRepository,
    FakeComissaoRepository,
)


def test_repository_can_save_an_atendimento(sqlite_session):
    b = barbeiro(id=1, nome="Ruan")
    sqlite_session.add(b)
    sqlite_session.commit()

    atendimento = Atendimento(
        id=1,
        barbeiro=b,
        servico=servico(id=1, nome="Corte", duracao=30, preco=50.0),
        data_hora=datetime(2026, 10, 5, 10, 0),
    )
    repo = SqlAlchemyAtendimentoRepository(sqlite_session)
    repo.add(atendimento)
    sqlite_session.commit()

    rows = list(
        sqlite_session.execute(
            text(
                "SELECT id, barbeiro_id, servico_nome, servico_duracao, servico_preco, status "
                "FROM atendimentos"
            )
        )
    )
    assert rows == [(1, 1, "Corte", 30, 50.0, "AGENDADO")]


def test_repository_can_retrieve_an_atendimento(sqlite_session):
    b = barbeiro(id=1, nome="Ruan")
    sqlite_session.add(b)
    sqlite_session.commit()

    atendimento = Atendimento(
        id=5,
        barbeiro=b,
        servico=servico(id=1, nome="Barba", duracao=15, preco=25.0),
        data_hora=datetime(2026, 10, 6, 14, 30),
        status=StatusAtendimento.CONCLUIDO,
    )
    repo = SqlAlchemyAtendimentoRepository(sqlite_session)
    repo.add(atendimento)
    sqlite_session.commit()
    sqlite_session.expunge_all()

    recuperado = repo.get(5)
    assert recuperado is not None
    assert recuperado.id == 5
    assert recuperado.barbeiro.id == 1
    assert recuperado.servico.nome == "Barba"
    assert recuperado.servico.duracao == 15
    assert recuperado.servico.preco == 25.0
    assert recuperado.status == StatusAtendimento.CONCLUIDO
    assert recuperado.concluido is True


def test_repository_can_save_and_retrieve_a_comissao(sqlite_session):
    b = barbeiro(id=1, nome="Ruan")
    sqlite_session.add(b)
    sqlite_session.commit()

    atendimento = Atendimento(
        id=1,
        barbeiro=b,
        servico=servico(id=1, nome="Corte", duracao=30, preco=50.0),
        data_hora=datetime(2026, 10, 5, 10, 0),
        status=StatusAtendimento.CONCLUIDO,
    )
    atendimento_repo = SqlAlchemyAtendimentoRepository(sqlite_session)
    atendimento_repo.add(atendimento)
    sqlite_session.commit()

    comissao = Comissao(id=1, atendimento=atendimento, percentual=20.0)
    comissao_repo = SqlAlchemyComissaoRepository(sqlite_session)
    comissao_repo.add(comissao)
    sqlite_session.commit()

    rows = list(
        sqlite_session.execute(
            text("SELECT id, barbeiro_id, atendimento_id, percentual_valor, valor FROM comissoes")
        )
    )
    assert rows == [(1, 1, 1, 20.0, 10.0)]

    sqlite_session.expunge_all()
    recuperada = comissao_repo.get(1)
    assert recuperada is not None
    assert recuperada.barbeiro.id == 1
    assert recuperada.atendimento.id == 1
    assert recuperada.percentual.valor == 20.0
    assert recuperada.valor == 10.0


def test_repository_list_comissoes_by_barbeiro(sqlite_session):
    b1 = barbeiro(id=1, nome="Ruan")
    b2 = barbeiro(id=2, nome="Outro")
    sqlite_session.add_all([b1, b2])
    sqlite_session.commit()

    atendimento_repo = SqlAlchemyAtendimentoRepository(sqlite_session)
    comissao_repo = SqlAlchemyComissaoRepository(sqlite_session)

    for atendimento_id, dono, preco in [(1, b1, 50.0), (2, b2, 80.0)]:
        atendimento = Atendimento(
            id=atendimento_id,
            barbeiro=dono,
            servico=servico(id=1, nome="Corte", duracao=30, preco=preco),
            data_hora=datetime(2026, 10, 5, 10, 0),
            status=StatusAtendimento.CONCLUIDO,
        )
        atendimento_repo.add(atendimento)
        sqlite_session.commit()
        comissao_repo.add(Comissao(id=atendimento_id, atendimento=atendimento))

    sqlite_session.commit()
    sqlite_session.expunge_all()

    do_barbeiro_1 = comissao_repo.list_by_barbeiro(1)
    assert len(do_barbeiro_1) == 1
    assert do_barbeiro_1[0].barbeiro.id == 1
    assert do_barbeiro_1[0].valor == 5.0


def test_fake_comissao_repository():
    b = barbeiro(id=1, nome="Ruan")
    atendimento = Atendimento(
        id=1,
        barbeiro=b,
        servico=servico(id=1, nome="Corte", duracao=30, preco=50.0),
        data_hora=datetime(2026, 10, 5, 10, 0),
        status=StatusAtendimento.CONCLUIDO,
    )
    comissao = Comissao(id=1, atendimento=atendimento)

    fake = FakeComissaoRepository()
    fake.add(comissao)

    assert fake.get(1) == comissao
    assert fake.get(999) is None
    assert fake.get_by_atendimento(1) == comissao
    assert fake.get_by_atendimento(999) is None
    assert fake.list() == [comissao]
    assert fake.list_by_barbeiro(1) == [comissao]
    assert fake.list_by_barbeiro(2) == []
