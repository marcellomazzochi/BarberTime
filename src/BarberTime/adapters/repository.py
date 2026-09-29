import abc
from BarberTime.domain.model import barbeiro

class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, item):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference):
        raise NotImplementedError


class AbstractBarbeiroRepository(AbstractRepository):
    @abc.abstractmethod
    def add(self, barbeiro: barbeiro):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, barbeiro_id: int) -> barbeiro:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list:
        raise NotImplementedError


class SqlAlchemyBarbeiroRepository(AbstractBarbeiroRepository):
    def __init__(self, session):
        self.session = session

    def add(self, barbeiro: barbeiro):
        self.session.add(barbeiro)

    def get(self, barbeiro_id: int):
        return self.session.query(barbeiro).filter_by(id=barbeiro_id).first()

    def list(self):
        return self.session.query(barbeiro).all()


class FakeBarbeiroRepository(AbstractBarbeiroRepository):
    def __init__(self, barbeiros=None):
        self._barbeiros = list(barbeiros) if barbeiros else []

    def add(self, barbeiro: barbeiro):
        self._barbeiros.append(barbeiro)

    def get(self, barbeiro_id: int):
        for b in self._barbeiros:
            if b.id == barbeiro_id:
                return b
        return None

    def list(self):
        return list(self._barbeiros)


BarbeiroRepository = SqlAlchemyBarbeiroRepository
FakeRepository = FakeBarbeiroRepository
