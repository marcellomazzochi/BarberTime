from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.orm import registry
from BarberTime.domain.model import barbeiro

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

def start_mappers():
    classes_mapeadas = {m.class_ for m in mapper_registry.mappers}
    if barbeiro not in classes_mapeadas:
        mapper_registry.map_imperatively(barbeiro, barbeiros)
