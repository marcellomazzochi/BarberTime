from datetime import datetime
from BarberTime.domain.model import barbeiro

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
