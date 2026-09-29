from dataclasses import dataclass
from datetime import datetime, time, timedelta

@dataclass(frozen=True)
class preco:
    valor: float

@dataclass(frozen=True)
class HorarioTrabalho:
    inicio: str = "08:00"
    fim: str = "18:00"

    def contem_horario(self, hora: time, duracao_minutos: int = 0) -> bool:
        t_inicio = datetime.strptime(self.inicio, "%H:%M").time()
        t_fim = datetime.strptime(self.fim, "%H:%M").time()
        if hora < t_inicio or hora > t_fim:
            return False
        if duracao_minutos > 0:
            dt_base = datetime.combine(datetime.today(), hora)
            dt_fim = (dt_base + timedelta(minutes=duracao_minutos)).time()
            if dt_fim > t_fim:
                return False
        return True

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
    def __init__(self, id, nome, horario_inicio="08:00", horario_fim="18:00", dias_trabalho="0,1,2,3,4,5"):
        self.id = id
        self.nome = nome
        self.horario_inicio = horario_inicio
        self.horario_fim = horario_fim
        self.dias_trabalho = dias_trabalho

    def _obter_dias_trabalho(self):
        if isinstance(self.dias_trabalho, str):
            return [int(d.strip()) for d in self.dias_trabalho.split(",") if d.strip()]
        return list(self.dias_trabalho)

    def pode_atender(self, data_hora, duracao_minutos: int = 0) -> bool:
        if isinstance(data_hora, str):
            data_hora = datetime.fromisoformat(data_hora)

        dias = self._obter_dias_trabalho()
        if data_hora.weekday() not in dias:
            return False

        t_inicio = datetime.strptime(self.horario_inicio, "%H:%M").time()
        t_fim = datetime.strptime(self.horario_fim, "%H:%M").time()
        hora_agendamento = data_hora.time()

        if hora_agendamento < t_inicio or hora_agendamento > t_fim:
            return False

        if duracao_minutos > 0:
            termino = (data_hora + timedelta(minutes=duracao_minutos)).time()
            if termino > t_fim:
                return False

        return True

    def validar_agendamento(self, data_hora, duracao_minutos: int = 0):
        if isinstance(data_hora, str):
            data_hora = datetime.fromisoformat(data_hora)

        dias = self._obter_dias_trabalho()
        if data_hora.weekday() not in dias:
            raise ValueError("Agendamento fora dos dias de trabalho do barbeiro")

        t_inicio = datetime.strptime(self.horario_inicio, "%H:%M").time()
        t_fim = datetime.strptime(self.horario_fim, "%H:%M").time()
        hora_agendamento = data_hora.time()

        if hora_agendamento < t_inicio:
            raise ValueError("Agendamento antes do inicio do expediente do barbeiro")

        if hora_agendamento > t_fim:
            raise ValueError("Agendamento apos o encerramento do expediente do barbeiro")

        if duracao_minutos > 0:
            termino = (data_hora + timedelta(minutes=duracao_minutos)).time()
            if termino > t_fim:
                raise ValueError("Duracao do atendimento ultrapassa o horario de encerramento do expediente")

    def adicionar_agendamento(self, agendamento):
        duracao = getattr(agendamento.servico, "duracao", 0) if hasattr(agendamento, "servico") else 0
        self.validar_agendamento(agendamento.data_hora, duracao)

    def alterar_expediente(self, novo_inicio: str, novo_fim: str):
        t_inicio = datetime.strptime(novo_inicio, "%H:%M").time()
        t_fim = datetime.strptime(novo_fim, "%H:%M").time()
        if t_inicio >= t_fim:
            raise ValueError("Horario de inicio deve ser anterior ao horario de fim")
        self.horario_inicio = novo_inicio
        self.horario_fim = novo_fim

    def __eq__(self, other):
        if not isinstance(other, barbeiro):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

Barbeiro = barbeiro

class Agendamento:
    def __init__(self, id, cliente, barbeiro, servico, data_hora):
        self.id = id
        self.cliente = cliente
        self.barbeiro = barbeiro
        self.servico = servico
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
