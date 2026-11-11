import pytest
from datetime import datetime
from BarberTime.domain.model import (
    cliente, servico, barbeiro, Agendamento, Agenda,
    ValidadorHorarioExato, ValidadorSuperposicaoHorario
)

def test_validador_horario_exato():
    b = barbeiro(id=1, nome="Carlos")
    c1 = cliente(id=1, nome="João")
    c2 = cliente(id=2, nome="Maria")
    s = servico(id=1, nome="Corte", duracao=30, preco=50.0)
    data = datetime(2026, 11, 20, 10, 0)

    ag1 = Agendamento(id=1, cliente=c1, barbeiro=b, servico=s, data_hora=data)
    ag2 = Agendamento(id=2, cliente=c2, barbeiro=b, servico=s, data_hora=data)

    agenda = Agenda(validador=ValidadorHorarioExato())
    agenda.adicionar_agendamento(ag1)

    with pytest.raises(ValueError, match="Horario indisponivel"):
        agenda.adicionar_agendamento(ag2)

def test_validador_superposicao_horario():
    b = barbeiro(id=1, nome="Carlos")
    c1 = cliente(id=1, nome="João")
    c2 = cliente(id=2, nome="Maria")
    s_longo = servico(id=1, nome="Barba + Barba", duracao=60, preco=80.0)
    s_curto = servico(id=2, nome="Pezinho", duracao=15, preco=20.0)

    inicio = datetime(2026, 11, 20, 14, 0)
    sobreposto = datetime(2026, 11, 20, 14, 30)

    ag1 = Agendamento(id=1, cliente=c1, barbeiro=b, servico=s_longo, data_hora=inicio)
    ag2 = Agendamento(id=2, cliente=c2, barbeiro=b, servico=s_curto, data_hora=sobreposto)

    agenda = Agenda(validador=ValidadorSuperposicaoHorario())
    agenda.adicionar_agendamento(ag1)

    with pytest.raises(ValueError, match="Horario em conflito com outro agendamento do barbeiro"):
        agenda.adicionar_agendamento(ag2)
