from datetime import datetime
from BarberTime.domain.model import barbeiro, Atendimento, Comissao, StatusAtendimento

def cadastrar_barbeiro(
    id: int,
    nome: str,
    horario_inicio: str = "08:00",
    horario_fim: str = "18:00",
    dias_trabalho: str = "0,1,2,3,4,5",
    repo=None,
    session=None,
) -> dict:
    if repo.get(id) is not None:
        raise ValueError(f"Barbeiro com id {id} ja cadastrado")

    novo_barbeiro = barbeiro(
        id=id,
        nome=nome,
        horario_inicio=horario_inicio,
        horario_fim=horario_fim,
        dias_trabalho=dias_trabalho,
    )
    repo.add(novo_barbeiro)
    if session is not None:
        session.commit()

    return {
        "id": novo_barbeiro.id,
        "nome": novo_barbeiro.nome,
        "horario_inicio": novo_barbeiro.horario_inicio,
        "horario_fim": novo_barbeiro.horario_fim,
        "dias_trabalho": novo_barbeiro.dias_trabalho,
    }

def consultar_barbeiro(barbeiro_id: int, repo) -> dict:
    b = repo.get(barbeiro_id)
    if b is None:
        raise ValueError(f"Barbeiro com id {barbeiro_id} nao encontrado")

    return {
        "id": b.id,
        "nome": b.nome,
        "horario_inicio": b.horario_inicio,
        "horario_fim": b.horario_fim,
        "dias_trabalho": b.dias_trabalho,
    }

def listar_barbeiros(repo) -> list[dict]:
    barbeiros = repo.list()
    return [
        {
            "id": b.id,
            "nome": b.nome,
            "horario_inicio": b.horario_inicio,
            "horario_fim": b.horario_fim,
            "dias_trabalho": b.dias_trabalho,
        }
        for b in barbeiros
    ]

def atualizar_expediente(
    barbeiro_id: int,
    novo_inicio: str,
    novo_fim: str,
    repo,
    session=None,
) -> dict:
    b = repo.get(barbeiro_id)
    if b is None:
        raise ValueError(f"Barbeiro com id {barbeiro_id} nao encontrado")

    b.alterar_expediente(novo_inicio, novo_fim)
    if session is not None:
        session.commit()

    return {
        "id": b.id,
        "nome": b.nome,
        "horario_inicio": b.horario_inicio,
        "horario_fim": b.horario_fim,
        "dias_trabalho": b.dias_trabalho,
    }

def validar_horario_atendimento(
    barbeiro_id: int,
    data_hora: str | datetime,
    duracao_minutos: int = 0,
    repo=None,
) -> dict:
    b = repo.get(barbeiro_id)
    if b is None:
        raise ValueError(f"Barbeiro com id {barbeiro_id} nao encontrado")

    b.validar_agendamento(data_hora, duracao_minutos)
    return {
        "valido": True,
        "barbeiro_id": b.id,
        "mensagem": "Horario disponivel no expediente do barbeiro",
    }


def _atendimento_para_dict(atendimento: Atendimento) -> dict:
    return {
        "id": atendimento.id,
        "barbeiro_id": atendimento.barbeiro.id if atendimento.barbeiro is not None else None,
        "servico": {
            "nome": atendimento.servico.nome,
            "duracao": atendimento.servico.duracao,
            "preco": atendimento.servico.preco,
        },
        "data_hora": atendimento.data_hora.isoformat() if atendimento.data_hora else None,
        "status": atendimento.status.value,
    }


def _comissao_para_dict(comissao: Comissao) -> dict:
    return {
        "id": comissao.id,
        "barbeiro_id": comissao.barbeiro.id if comissao.barbeiro is not None else None,
        "atendimento_id": comissao.atendimento.id,
        "percentual": comissao.percentual.valor,
        "valor": comissao.valor,
    }


def registrar_atendimento(
    atendimento_id: int,
    barbeiro_id: int,
    servico,
    data_hora,
    atendimento_repo,
    barbeiro_repo,
    session=None,
) -> dict:
    if atendimento_repo.get(atendimento_id) is not None:
        raise ValueError(f"Atendimento com id {atendimento_id} ja cadastrado")

    b = barbeiro_repo.get(barbeiro_id)
    if b is None:
        raise ValueError(f"Barbeiro com id {barbeiro_id} nao encontrado")

    atendimento = Atendimento(
        id=atendimento_id,
        barbeiro=b,
        servico=servico,
        data_hora=data_hora,
    )
    atendimento_repo.add(atendimento)
    if session is not None:
        session.commit()

    return _atendimento_para_dict(atendimento)


def concluir_atendimento(atendimento_id: int, atendimento_repo, session=None) -> dict:
    atendimento = atendimento_repo.get(atendimento_id)
    if atendimento is None:
        raise ValueError(f"Atendimento com id {atendimento_id} nao encontrado")

    atendimento.concluir()
    if session is not None:
        session.commit()

    return _atendimento_para_dict(atendimento)


def consultar_atendimento(atendimento_id: int, repo) -> dict:
    atendimento = repo.get(atendimento_id)
    if atendimento is None:
        raise ValueError(f"Atendimento com id {atendimento_id} nao encontrado")
    return _atendimento_para_dict(atendimento)


def gerar_comissao(
    comissao_id: int,
    atendimento_id: int,
    atendimento_repo,
    comissao_repo,
    percentual=None,
    session=None,
) -> dict:
    if comissao_repo.get(comissao_id) is not None:
        raise ValueError(f"Comissao com id {comissao_id} ja cadastrada")

    atendimento = atendimento_repo.get(atendimento_id)
    if atendimento is None:
        raise ValueError(f"Atendimento com id {atendimento_id} nao encontrado")

    if comissao_repo.get_by_atendimento(atendimento_id) is not None:
        raise ValueError(
            f"Ja existe comissao gerada para o atendimento {atendimento_id}"
        )

    comissao = Comissao(id=comissao_id, atendimento=atendimento, percentual=percentual)
    comissao_repo.add(comissao)
    if session is not None:
        session.commit()

    return _comissao_para_dict(comissao)


def consultar_comissao(comissao_id: int, repo) -> dict:
    comissao = repo.get(comissao_id)
    if comissao is None:
        raise ValueError(f"Comissao com id {comissao_id} nao encontrada")
    return _comissao_para_dict(comissao)


def listar_comissoes(repo) -> list[dict]:
    return [_comissao_para_dict(c) for c in repo.list()]


def listar_comissoes_por_barbeiro(barbeiro_id: int, repo) -> list[dict]:
    return [_comissao_para_dict(c) for c in repo.list_by_barbeiro(barbeiro_id)]
