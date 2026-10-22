from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from BarberTime.adapters.orm import metadata, start_mappers
from BarberTime.adapters.repository import SqlAlchemyFidelidadeRepository
from BarberTime.domain.model import Fidelidade


def test_fidelidade_pode_ser_salva_e_consultada():
    start_mappers()

    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    with Session() as session:
        repositorio = SqlAlchemyFidelidadeRepository(session)

        fidelidade = Fidelidade(
            id=1,
            cliente_id=100,
            cortes_concluidos=5,
            cortes_para_gratis=10,
        )

        repositorio.add(fidelidade)
        session.commit()

        recuperada = repositorio.get_by_cliente(100)

        assert recuperada is not None
        assert recuperada.id == 1
        assert recuperada.cliente_id == 100
        assert recuperada.cortes_concluidos == 5
        assert recuperada.cortes_para_gratis == 10

    engine.dispose()


def test_fidelidade_pode_ser_buscada_por_id():
    start_mappers()

    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    with Session() as session:
        repositorio = SqlAlchemyFidelidadeRepository(session)

        fidelidade = Fidelidade(
            id=2,
            cliente_id=200,
            cortes_concluidos=3,
        )

        repositorio.add(fidelidade)
        session.commit()

        recuperada = repositorio.get(2)

        assert recuperada is not None
        assert recuperada.cliente_id == 200
        assert recuperada.cortes_concluidos == 3

    engine.dispose()
