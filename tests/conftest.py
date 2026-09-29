import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from BarberTime.adapters import orm

@pytest.fixture
def in_memory_sqlite_db():
    engine = create_engine("sqlite:///:memory:")
    orm.metadata.create_all(engine)
    orm.start_mappers()
    yield engine
    clear_mappers()

@pytest.fixture
def sqlite_session(in_memory_sqlite_db):
    start_session = sessionmaker(bind=in_memory_sqlite_db)
    session = start_session()
    yield session
    session.close()

@pytest.fixture
def client(in_memory_sqlite_db):
    from BarberTime.entrypoints import flask_app
    original_get_session = flask_app.get_session
    flask_app.get_session = sessionmaker(bind=in_memory_sqlite_db)
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as test_client:
        yield test_client
    flask_app.get_session = original_get_session
