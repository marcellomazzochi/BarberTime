from __future__ import annotations
import abc
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
        
@dataclass(frozen=True)
class JornadaTrabalho:
    horario_inicio: str = "08:00"
    horario_fim: str = "18:00"
    dias_trabalho: str = "0,1,2,3,4,5"

    def obter_dias(self) -> list[int]:
        if isinstance(self.dias_trabalho, str):
            return [int(d.strip()) for d in self.dias_trabalho.split(",") if d.strip()]
        return list(self.dias_trabalho)

    def contem_dia(self, data_hora: datetime | str) -> bool:
        if isinstance(data_hora, str):
            data_hora = datetime.fromisoformat(data_hora)
        return data_hora.weekday() in self.obter_dias()

    def contem_horario(self, data_hora: datetime | str, duracao_minutos: int = 0) -> bool:
        if isinstance(data_hora, str):
            data_hora = datetime.fromisoformat(data_hora)
        if not self.contem_dia(data_hora):
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

    def validar_atendimento(self, data_hora: datetime | str, duracao_minutos: int = 0) -> None:
        if isinstance(data_hora, str):
            data_hora = datetime.fromisoformat(data_hora)

        if not self.contem_dia(data_hora):
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

    def com_novo_expediente(self, novo_inicio: str, novo_fim: str) -> "JornadaTrabalho":
        t_inicio = datetime.strptime(novo_inicio, "%H:%M").time()
        t_fim = datetime.strptime(novo_fim, "%H:%M").time()
        if t_inicio >= t_fim:
            raise ValueError("Horario de inicio deve ser anterior ao horario de fim")
        return JornadaTrabalho(
            horario_inicio=novo_inicio,
            horario_fim=novo_fim,
            dias_trabalho=self.dias_trabalho,
        )


class barbeiro:
    def __init__(
        self,
        id,
        nome,
        horario_inicio="08:00",
        horario_fim="18:00",
        dias_trabalho="0,1,2,3,4,5",
        jornada: JornadaTrabalho | None = None,
    ):
        self.id = id
        self.nome = nome
        if jornada is not None:
            self.jornada = jornada
        else:
            self.horario_inicio = horario_inicio
            self.horario_fim = horario_fim
            self.dias_trabalho = dias_trabalho
            self._jornada = JornadaTrabalho(
                horario_inicio=horario_inicio,
                horario_fim=horario_fim,
                dias_trabalho=dias_trabalho,
            )

    @property
    def jornada(self) -> JornadaTrabalho:
        h_inicio = getattr(self, "horario_inicio", "08:00")
        h_fim = getattr(self, "horario_fim", "18:00")
        d_trabalho = getattr(self, "dias_trabalho", "0,1,2,3,4,5")
        if (
            not hasattr(self, "_jornada")
            or self._jornada is None
            or self._jornada.horario_inicio != h_inicio
            or self._jornada.horario_fim != h_fim
            or self._jornada.dias_trabalho != d_trabalho
        ):
            self._jornada = JornadaTrabalho(
                horario_inicio=h_inicio,
                horario_fim=h_fim,
                dias_trabalho=d_trabalho,
            )
        return self._jornada

    @jornada.setter
    def jornada(self, nova_jornada: JornadaTrabalho):
        self._jornada = nova_jornada
        self.horario_inicio = nova_jornada.horario_inicio
        self.horario_fim = nova_jornada.horario_fim
        self.dias_trabalho = nova_jornada.dias_trabalho

    def _obter_dias_trabalho(self):
        return self.jornada.obter_dias()

    def pode_atender(self, data_hora, duracao_minutos: int = 0) -> bool:
        return self.jornada.contem_horario(data_hora, duracao_minutos)

    def validar_agendamento(self, data_hora, duracao_minutos: int = 0):
        self.jornada.validar_atendimento(data_hora, duracao_minutos)

    def adicionar_agendamento(self, agendamento):
        duracao = getattr(agendamento.servico, "duracao", 0) if hasattr(agendamento, "servico") else 0
        self.validar_agendamento(agendamento.data_hora, duracao)

    def alterar_expediente(self, novo_inicio: str, novo_fim: str):
        self.jornada = self.jornada.com_novo_expediente(novo_inicio, novo_fim)

    def definir_jornada(self, nova_jornada: JornadaTrabalho):
        self.jornada = nova_jornada

    def __eq__(self, other):
        if not isinstance(other, barbeiro):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

Barbeiro = barbeiro

class RegraDisponibilidade:
    def validar(self, agendamento, agendamentos_existentes):
        raise NotImplementedError

class ValidadorHorarioExato(RegraDisponibilidade):
    def validar(self, agendamento, agendamentos_existentes):
        horario = (agendamento.barbeiro, agendamento.data_hora)
        if horario in agendamentos_existentes:
            raise ValueError("Horario indisponivel")

class Agendamento:
    def __init__(self, id, cliente, barbeiro, servico, data_hora):
        self.id = id
        self.cliente = cliente
        self.barbeiro = barbeiro
        self.servico = servico
        self.data_hora = data_hora
        self.status = "Agendado"

class Agenda:
    def __init__(self, validador: RegraDisponibilidade = None):
        self.agendamentos = {}
        self.validador = validador or ValidadorHorarioExato()

    def adicionar_agendamento(self, agendamento):
        self.validador.validar(agendamento, self.agendamentos)
        horario = (agendamento.barbeiro, agendamento.data_hora)
        self.agendamentos[horario] = agendamento
        
from enum import Enum


class StatusAtendimento(Enum):
    AGENDADO = "Agendado"
    CONCLUIDO = "Concluido"
    CANCELADO = "Cancelado"
    FALTOU = "Faltou"


@dataclass(frozen=True)
class PercentualComissao:
    valor: float

    def __post_init__(self):
        if not isinstance(self.valor, (int, float)) or isinstance(self.valor, bool):
            raise ValueError("Percentual de comissao deve ser um numero")
        if self.valor <= 0 or self.valor > 100:
            raise ValueError("Percentual de comissao deve ser maior que 0 e menor ou igual a 100")

    def aplicar(self, valor_base: float) -> float:
        return round(float(valor_base) * self.valor / 100.0, 2)


@dataclass(frozen=True)
class ServicoRealizado:
    nome: str
    duracao: int = 0
    preco: float = 0.0


def _valor_preco(preco) -> float:
    if hasattr(preco, "valor"):
        return float(preco.valor)
    return float(preco)


def _normalizar_servico(servico) -> ServicoRealizado:
    if isinstance(servico, ServicoRealizado):
        return servico
    if isinstance(servico, dict):
        return ServicoRealizado(
            nome=servico.get("nome", ""),
            duracao=servico.get("duracao", 0),
            preco=_valor_preco(servico.get("preco", 0)),
        )
    return ServicoRealizado(
        nome=getattr(servico, "nome", ""),
        duracao=getattr(servico, "duracao", 0),
        preco=_valor_preco(getattr(servico, "preco", 0)),
    )


def _normalizar_data_hora(data_hora) -> datetime:
    if isinstance(data_hora, str):
        return datetime.fromisoformat(data_hora)
    return data_hora


class Atendimento:
    def __init__(self, id, barbeiro, servico, data_hora, status=StatusAtendimento.AGENDADO):
        self.id = id
        self.barbeiro = barbeiro
        self.servico = _normalizar_servico(servico)
        self.data_hora = _normalizar_data_hora(data_hora)
        self.status = status if isinstance(status, StatusAtendimento) else StatusAtendimento(status)

    @property
    def concluido(self) -> bool:
        return self.status == StatusAtendimento.CONCLUIDO

    def pode_gerar_comissao(self) -> bool:
        return self.concluido

    def concluir(self):
        if self.status == StatusAtendimento.CANCELADO:
            raise ValueError("Atendimento cancelado nao pode ser concluido")
        self.status = StatusAtendimento.CONCLUIDO
        return self

    def cancelar(self):
        if self.status == StatusAtendimento.CONCLUIDO:
            raise ValueError("Atendimento ja concluido nao pode ser cancelado")
        self.status = StatusAtendimento.CANCELADO
        return self

    def marcar_falta(self):
        if self.status == StatusAtendimento.CONCLUIDO:
            raise ValueError("Atendimento ja concluido nao pode ser marcado como falta")
        self.status = StatusAtendimento.FALTOU
        return self

    def __eq__(self, other):
        if not isinstance(other, Atendimento):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


# ---------------------------------------------------------------------------
# OCP — Strategy de Calculo de Comissao
# ---------------------------------------------------------------------------
class EstrategiaComissao(abc.ABC):
    """Interface (Strategy) para calcular o valor da comissao."""

    @abc.abstractmethod
    def calcular(self, preco_servico: float) -> float:
        raise NotImplementedError


class ComissaoPercentualFixo(EstrategiaComissao):
    """Estrategia padrao: percentual fixo sobre o preco do servico."""

    def __init__(self, percentual: float | PercentualComissao = 10.0):
        if isinstance(percentual, PercentualComissao):
            self._percentual = percentual
        else:
            self._percentual = PercentualComissao(percentual)

    @property
    def percentual(self) -> PercentualComissao:
        return self._percentual

    def calcular(self, preco_servico: float) -> float:
        return self._percentual.aplicar(preco_servico)


class ComissaoBarbeiroSenior(EstrategiaComissao):
    """Estrategia para barbeiros seniors: 15% fixo, sem desconto de insumos."""

    _PERCENTUAL = PercentualComissao(15.0)

    def calcular(self, preco_servico: float) -> float:
        return self._PERCENTUAL.aplicar(preco_servico)


class ComissaoBarbeiroJunior(EstrategiaComissao):
    """Estrategia para barbeiros juniores: 10% com desconto de R$ 5,00 de insumos."""

    _PERCENTUAL = PercentualComissao(10.0)
    DESCONTO_INSUMOS: float = 5.0

    def calcular(self, preco_servico: float) -> float:
        bruto = self._PERCENTUAL.aplicar(preco_servico)
        return round(max(0.0, bruto - self.DESCONTO_INSUMOS), 2)


# ---------------------------------------------------------------------------

class Comissao:
    def __init__(
        self,
        id,
        atendimento,
        percentual=None,
        barbeiro=None,
        estrategia: EstrategiaComissao | None = None,
    ):
        if atendimento is None:
            raise ValueError("Atendimento e obrigatorio para gerar comissao")

        if not atendimento.concluido:
            raise ValueError(
                "Nao e possivel gerar comissao para atendimento nao concluido"
            )

        barbeiro = barbeiro if barbeiro is not None else atendimento.barbeiro
        if atendimento.barbeiro is not None and barbeiro != atendimento.barbeiro:
            raise ValueError("Atendimento nao pertence ao barbeiro informado")

        if estrategia is not None:
            self._estrategia = estrategia
            if isinstance(estrategia, ComissaoPercentualFixo):
                self.percentual = estrategia.percentual
            else:
                self.percentual = None
        else:
            if percentual is None:
                percentual = PercentualComissao(10.0)
            elif not isinstance(percentual, PercentualComissao):
                percentual = PercentualComissao(percentual)
            self._estrategia = ComissaoPercentualFixo(percentual)
            self.percentual = percentual

        self.id = id
        self.atendimento = atendimento
        self.barbeiro = barbeiro
        self.valor = self._estrategia.calcular(atendimento.servico.preco)

    def __eq__(self, other):
        if not isinstance(other, Comissao):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)



class Fidelidade:

    def __init__(
        self,
        id,
        cliente_id,
        cortes_concluidos=0,
        historico_atendimentos=None,
        cortes_para_gratis=10,
    ):
        if id is None or cliente_id is None:
            raise ValueError(
                "ID da fidelidade e ID do cliente são obrigatórios"
            )

        if (
            isinstance(cortes_concluidos, bool)
            or not isinstance(cortes_concluidos, int)
            or cortes_concluidos < 0
        ):
            raise ValueError(
                "A quantidade de cortes deve ser um inteiro não negativo"
            )

        if (
            isinstance(cortes_para_gratis, bool)
            or not isinstance(cortes_para_gratis, int)
            or cortes_para_gratis <= 0
        ):
            raise ValueError(
                "A meta de cortes deve ser um inteiro positivo"
            )

        self.id = id
        self.cliente_id = cliente_id
        self.cortes_concluidos = cortes_concluidos
        self.historico_atendimentos = list(
            historico_atendimentos or []
        )
        self.cortes_para_gratis = cortes_para_gratis
        self._possui_no_show = False

    @property
    def possui_no_show(self):
        """Verifica se existe no-show no histórico ou no estado persistido."""
        historico = getattr(self, "historico_atendimentos", [])

        return getattr(self, "_possui_no_show", False) or any(
            atendimento.status == StatusAtendimento.FALTOU
            for atendimento in historico
        )

    @property
    def corte_gratis_disponivel(self):
        """Verifica se o cliente acumulou cortes suficientes."""
        return self.cortes_concluidos >= self.cortes_para_gratis

    @property
    def cortes_restantes(self):
        """Retorna quantos cortes faltam para atingir a meta."""
        return max(
            0,
            self.cortes_para_gratis - self.cortes_concluidos
        )

    def registrar_corte_concluido(self):
        """Registra um corte concluído no progresso da fidelidade."""
        self.cortes_concluidos += 1
        return self
    
    def registrar_no_show(self):
        """Registra um no-show e bloqueia o resgate do benefício."""
        self._possui_no_show = True
        return self

    def pode_resgatar_corte_gratis(self):
        """Verifica se o cliente pode resgatar o benefício."""
        return (
            self.corte_gratis_disponivel
            and not self.possui_no_show
        )

    def resgatar_corte_gratis(self):
        """Resgata o benefício se todas as regras forem atendidas."""
        if self.possui_no_show:
            raise ValueError(
                "Resgate negado: cliente possui no-show no histórico"
            )

        if not self.corte_gratis_disponivel:
            raise ValueError(
                "Resgate negado: cliente ainda não acumulou cortes suficientes"
            )

        self.cortes_concluidos -= self.cortes_para_gratis
        return self

    def __eq__(self, other):
        if not isinstance(other, Fidelidade):
            return False

        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
