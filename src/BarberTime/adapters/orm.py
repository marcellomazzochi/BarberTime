from sqlalchemy import Table, Column, Integer, String, Float, DateTime, ForeignKey, Enum as SqlEnum, MetaData
from sqlalchemy.orm import registry, relationship, composite
from BarberTime.domain.model import (
    barbeiro,
    Atendimento,
    Comissao,
    ServicoRealizado,
    PercentualComissao,
    StatusAtendimento,
)

metadata = MetaData()
mapper_registry = registry()

barbeiros = Table(
    "barbeiros",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String(255), nullable=False),
    Column("horario_inicio", String(5), default="08:00"),
    Column("horario_fim", String(5), default="18:00"),
    Column("dias_trabalho", String(50), default="0,1,2,3,4,5"),
)

atendimentos = Table(
    "atendimentos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("barbeiro_id", Integer, ForeignKey("barbeiros.id"), nullable=False),
    Column("servico_nome", String(255), nullable=False, default=""),
    Column("servico_duracao", Integer, nullable=False, default=0),
    Column("servico_preco", Float, nullable=False, default=0.0),
    Column("data_hora", DateTime, nullable=False),
    Column("status", SqlEnum(StatusAtendimento), nullable=False, default=StatusAtendimento.AGENDADO),
)

comissoes = Table(
    "comissoes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("barbeiro_id", Integer, ForeignKey("barbeiros.id"), nullable=False),
    Column("atendimento_id", Integer, ForeignKey("atendimentos.id"), nullable=False, unique=True),
    Column("percentual_valor", Float, nullable=False),
    Column("valor", Float, nullable=False),
)

def start_mappers():
    classes_mapeadas = {m.class_ for m in mapper_registry.mappers}
    if barbeiro not in classes_mapeadas:
        mapper_registry.map_imperatively(barbeiro, barbeiros)
    if Atendimento not in classes_mapeadas:
        mapper_registry.map_imperatively(
            Atendimento,
            atendimentos,
            properties={
                "barbeiro": relationship(barbeiro),
                "servico": composite(
                    ServicoRealizado,
                    atendimentos.c.servico_nome,
                    atendimentos.c.servico_duracao,
                    atendimentos.c.servico_preco,
                ),
            },
        )
    if Comissao not in classes_mapeadas:
        mapper_registry.map_imperatively(
            Comissao,
            comissoes,
            properties={
                "barbeiro": relationship(barbeiro),
                "atendimento": relationship(Atendimento),
                "percentual": composite(PercentualComissao, comissoes.c.percentual_valor),
            },
        )
