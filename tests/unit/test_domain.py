import pytest

from datetime import datetime

from BarberTime.domain.model import cliente, servico, barbeiro, Agendamento, Agenda

barbeiro1 = barbeiro(id=10, nome="Junior")
servico1 = servico(id=1, nome="Corte", duracao=30, preco=50.0)
data = datetime.now()

def teste_agendar_cliente():

    cliente1 = cliente(id=100, nome="João")
