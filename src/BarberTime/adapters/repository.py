import abc
from BarberTime.domain.model import barbeiro, Atendimento, Comissao

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


class AbstractAtendimentoRepository(AbstractRepository):
    @abc.abstractmethod
    def add(self, atendimento: Atendimento):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, atendimento_id: int) -> Atendimento:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list:
        raise NotImplementedError


class SqlAlchemyAtendimentoRepository(AbstractAtendimentoRepository):
    def __init__(self, session):
        self.session = session

    def add(self, atendimento: Atendimento):
        self.session.add(atendimento)

    def get(self, atendimento_id: int):
        return self.session.query(Atendimento).filter_by(id=atendimento_id).first()

    def list(self):
        return self.session.query(Atendimento).all()


class FakeAtendimentoRepository(AbstractAtendimentoRepository):
    def __init__(self, atendimentos=None):
        self._atendimentos = list(atendimentos) if atendimentos else []

    def add(self, atendimento: Atendimento):
        self._atendimentos.append(atendimento)

    def get(self, atendimento_id: int):
        for a in self._atendimentos:
            if a.id == atendimento_id:
                return a
        return None

    def list(self):
        return list(self._atendimentos)


class AbstractComissaoRepository(AbstractRepository):
    @abc.abstractmethod
    def add(self, comissao: Comissao):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, comissao_id: int) -> Comissao:
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_atendimento(self, atendimento_id: int) -> Comissao:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list:
        raise NotImplementedError

    @abc.abstractmethod
    def list_by_barbeiro(self, barbeiro_id: int) -> list:
        raise NotImplementedError


class SqlAlchemyComissaoRepository(AbstractComissaoRepository):
    def __init__(self, session):
        self.session = session

    def add(self, comissao: Comissao):
        self.session.add(comissao)

    def get(self, comissao_id: int):
        return self.session.query(Comissao).filter_by(id=comissao_id).first()

    def get_by_atendimento(self, atendimento_id: int):
        return (
            self.session.query(Comissao)
            .filter_by(atendimento_id=atendimento_id)
            .first()
        )

    def list(self):
        return self.session.query(Comissao).all()

    def list_by_barbeiro(self, barbeiro_id: int):
        return self.session.query(Comissao).filter_by(barbeiro_id=barbeiro_id).all()


class FakeComissaoRepository(AbstractComissaoRepository):
    def __init__(self, comissoes=None):
        self._comissoes = list(comissoes) if comissoes else []

    def add(self, comissao: Comissao):
        self._comissoes.append(comissao)

    def get(self, comissao_id: int):
        for c in self._comissoes:
            if c.id == comissao_id:
                return c
        return None

    def get_by_atendimento(self, atendimento_id: int):
        for c in self._comissoes:
            if getattr(c.atendimento, "id", None) == atendimento_id:
                return c
        return None

    def list(self):
        return list(self._comissoes)

    def list_by_barbeiro(self, barbeiro_id: int):
        return [c for c in self._comissoes if getattr(c.barbeiro, "id", None) == barbeiro_id]


BarbeiroRepository = SqlAlchemyBarbeiroRepository
FakeRepository = FakeBarbeiroRepository
AtendimentoRepository = SqlAlchemyAtendimentoRepository
ComissaoRepository = SqlAlchemyComissaoRepository
FakeAtendimentoRepo = FakeAtendimentoRepository
FakeComissaoRepo = FakeComissaoRepository
