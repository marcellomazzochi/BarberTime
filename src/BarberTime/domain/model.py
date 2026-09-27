class cliente:
    def __init__(self, id, nome):
        self.id = id
        self.nome = nome
        
class servico: 
    def __init__(self, id, nome, duracao, preco):
        self.id = id
        self.nome = nome
        self.duracao = duracao
        self.preco = preco 
        
class barbeiro:
    def __init__(self, id, nome):
        self.id = id
        self.nome = nome
        
class Agendamento:
    def __init__(self, id, cliente, barbeiro, servicos, data_hora):
        self.id = id
        self.cliente = cliente
        self.barbeiro = barbeiro
        self.servicos = servicos
        self.data_hora = data_hora
        self.status = "Agendado"

class Agenda:
    def __init__(self):
        self.agendamentos = {}

    def adicionar_agendamento(self, agendamento):
        horario = (agendamento.barbeiro, agendamento.data_hora)
        
        if horario in self.agendamentos:
            raise ValueError("Horario indisponivel")

        self.agendamentos[horario] = agendamento
