import pytest
from sqlalchemy import text
from BarberTime.domain.model import barbeiro
from BarberTime.adapters.repository import (
    SqlAlchemyBarbeiroRepository,
    FakeBarbeiroRepository,
)

def test_repository_can_save_a_barbeiro(sqlite_session):
    b = barbeiro(
        id=1,
        nome="Jonathan Melo",
        horario_inicio="08:30",
        horario_fim="17:30",
        dias_trabalho="0,1,2,3,4",
    )
    repo = SqlAlchemyBarbeiroRepository(sqlite_session)
    repo.add(b)
    sqlite_session.commit()

    rows = list(
        sqlite_session.execute(
            text("SELECT id, nome, horario_inicio, horario_fim, dias_trabalho FROM barbeiros")
        )
    )
    assert rows == [(1, "Jonathan Melo", "08:30", "17:30", "0,1,2,3,4")]

def test_repository_can_retrieve_a_barbeiro(sqlite_session):
    sqlite_session.execute(
        text(
            "INSERT INTO barbeiros (id, nome, horario_inicio, horario_fim, dias_trabalho) "
            "VALUES (2, 'Carlos Barbeiro', '09:00', '18:00', '0,1,2,3,4,5')"
        )
    )
    sqlite_session.commit()

    repo = SqlAlchemyBarbeiroRepository(sqlite_session)
    retrieved = repo.get(2)

    assert retrieved is not None
    assert retrieved.id == 2
    assert retrieved.nome == "Carlos Barbeiro"
    assert retrieved.horario_inicio == "09:00"
    assert retrieved.horario_fim == "18:00"
    assert retrieved.dias_trabalho == "0,1,2,3,4,5"

def test_repository_list_barbeiros(sqlite_session):
    b1 = barbeiro(id=1, nome="Jonathan")
    b2 = barbeiro(id=2, nome="Marcello")
    repo = SqlAlchemyBarbeiroRepository(sqlite_session)
    repo.add(b1)
    repo.add(b2)
    sqlite_session.commit()

    barbeiros_salvos = repo.list()
    assert len(barbeiros_salvos) == 2
    ids = {b.id for b in barbeiros_salvos}
    assert ids == {1, 2}

def test_fake_barbeiro_repository():
    fake_repo = FakeBarbeiroRepository()
    b = barbeiro(id=1, nome="Jonathan", horario_inicio="08:00", horario_fim="18:00")
    fake_repo.add(b)

    assert fake_repo.get(1) == b
    assert fake_repo.get(999) is None
    assert fake_repo.list() == [b]
