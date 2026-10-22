# ADR 0002 — Mapeamento Imperativo com SQLAlchemy para Preservar o Domínio Puro

| Campo | Valor |
|---|---|
| **Status** | Aceita |
| **Data** | 2026-10-22 |
| **Autores** | Jonathan do Nascimento Melo (Colega 1) |
| **Tema** | Arquitetura de Persistência, Isolamento de Infraestrutura e Pureza do Modelo de Domínio |

---

## Contexto

No desenvolvimento do **BarberTime**, o sistema precisava persistir agregados de negócio — inicialmente `barbeiro` e `Agenda`, e posteriormente `Atendimento`, `Comissao` e `Fidelidade` — em banco de dados relacional (SQLite via SQLAlchemy).

O problema central que motivou esta decisão foi a **contaminação do modelo de domínio pela infraestrutura de persistência do ORM**.

No ecossistema Python com SQLAlchemy, a abordagem mais comum e amplamente documentada é o mapeamento declarativo (*Declarative Mapping* / estilo *Active Record*), no qual as classes de negócio herdam de uma classe base do ORM (`DeclarativeBase` ou `declarative_base()`):

```python
# Abordagem declarativa padrao do SQLAlchemy (REJEITADA)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Barbeiro(Base):
    __tablename__ = "barbeiros"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column()
    # A classe de negocio herda o runtime do SQLAlchemy, metadados de tabela e estado de sessao
```

Se tivéssemos adotado essa abordagem declarativa convencional, enfrentaríamos três problemas graves de projeto:

1. **Acoplamento do núcleo de negócio a um framework externo:** As classes de domínio deixariam de ser objetos Python puros (*Plain Old Python Objects* ou dataclasses simples) e ficariam acopladas ao SQLAlchemy. Qualquer refatoração de regras de negócio, testes ou até mesmo a migração futura para outro mecanismo de armazenamento exigiria mexer em definições atreladas à infraestrutura de banco de dados.
2. **Degradação da testabilidade unitária:** Entidades que herdam de `DeclarativeBase` possuem comportamentos de ciclo de vida atrelados a uma `Session` ativa (como instrumentação de atributos, lazy loading implícito e erros de `DetachedInstanceError`). Testar a regra de negócio do barbeiro (por exemplo, "rejeitar agendamento fora do expediente de trabalho" ou "validar corte que ultrapassa o horário de fechamento") exigiria instanciar o mecanismo do SQLAlchemy mesmo em testes puramente de unidade.
3. **Dificuldade de modelar Value Objects puros:** O domínio do BarberTime possui conceitos imutáveis sem identidade própria (Value Objects), tais como `HorarioTrabalho`, `ServicoRealizado` e `PercentualComissao`. No modelo declarativo, esses conceitos tendem a ser degradados a colunas primitivas soltas na tabela (`hora_inicio`, `hora_fim`, `percentual_valor`) ou exigir heranças artificiais de tabelas separadas.

Era fundamental garantir que o modelo de domínio permanecesse 100% puro e focado exclusivamente nas invariantes de negócio.

---

## Decisão

Adotamos o **Mapeamento Imperativo** (*Classical Mapping* via `mapper_registry.map_imperatively`, conforme preconizado pelo livro *Architecture Patterns with Python*, Capítulo 2) em `src/BarberTime/adapters/orm.py`.

A arquitetura estabelece uma separação física e conceitual estrita:

1. **Domínio Puro (`src/BarberTime/domain/model.py`):**
   - As classes `barbeiro`, `HorarioTrabalho`, `Agenda`, `Atendimento`, `Comissao` e `Fidelidade` não herdam de nenhuma classe de biblioteca externa.
   - O arquivo importa estritamente módulos da biblioteca padrão do Python (`dataclasses`, `datetime`, `enum`, `typing`).
   - As regras de negócio e validações de invariantes residem no próprio domínio através de construtores ricos e métodos de negócio.

2. **Tabelas Relacionais e Mapeamento (`src/BarberTime/adapters/orm.py`):**
   - As tabelas são definidas como objetos `Table` puros vinculados a um `MetaData()` central.
   - A função `start_mappers()` invoca `mapper_registry.map_imperatively()` para conectar a classe de domínio à tabela correspondente.
   - Objetos de Valor são mapeados através de `composite()`, associando colunas relacionais a dataclasses imutáveis.

### Implementação Concreta no Agregado Barbeiro

```python
# 1. No dominio (src/BarberTime/domain/model.py) — Python Puro
@dataclass(frozen=True)
class HorarioTrabalho:
    inicio: time = time(8, 0)
    fim: time = time(18, 0)

class barbeiro:
    def __init__(self, id: int, nome: str, horario_trabalho: HorarioTrabalho = None):
        self.id = id
        self.nome = nome
        self.horario_trabalho = horario_trabalho or HorarioTrabalho()

    def pode_atender(self, data_hora: datetime, duracao_minutos: int = 30) -> bool:
        # Invariante de negocio pura: valida se o atendimento cabe no expediente
        ...
```

```python
# 2. No adaptador ORM (src/BarberTime/adapters/orm.py) — Infraestrutura Isolada
metadata = MetaData()
mapper_registry = registry(metadata=metadata)

barbeiros = Table(
    "barbeiros",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String(100), nullable=False),
    Column("inicio_expediente", Time, nullable=True),
    Column("fim_expediente", Time, nullable=True),
    Column("dias_trabalho", String(50), nullable=True),
)

def start_mappers():
    if mapper_registry.mappers:
        return
    mapper_registry.map_imperatively(
        model.barbeiro,
        barbeiros,
        properties={
            "horario_trabalho": composite(
                model.HorarioTrabalho,
                barbeiros.c.inicio_expediente,
                barbeiros.c.fim_expediente,
            )
        },
    )
```

Essa separação garante que a inicialização do ORM ocorra apenas quando a aplicação real (Flask) ou os testes de integração forem iniciados, mantendo o domínio totalmente independente.

---

## Alternativas Consideradas

### Alternativa 1 — Mapeamento Declarativo Padrão (`DeclarativeBase` / estilo Active Record)

Consistiria em fazer as classes de modelo herdarem de `DeclarativeBase` do SQLAlchemy 2.0, definindo colunas e relacionamentos diretamente no corpo das entidades.

```python
# DESCARTADO — Exemplo hipotético
class Barbeiro(Base):
    __tablename__ = "barbeiros"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100))
    inicio_expediente = Column(Time)
    fim_expediente = Column(Time)

    def pode_atender(self, data_hora, duracao):
        # Mistura de métodos de negócio com metadados do ORM
        ...
```

**Por que foi descartado:**
- Viola o princípio de inversão de dependências e a arquitetura *Ports & Adapters*: o núcleo da aplicação dependeria diretamente de uma biblioteca externa de persistência.
- Impossibilita testes unitários rápidos e puros sem arrastar a infraestrutura do SQLAlchemy.
- Cria dependência de estado de sessão do SQLAlchemy dentro dos objetos de negócio, gerando potenciais erros de concorrência ou atributos não carregados fora da sessão HTTP.

---

### Alternativa 2 — Persistência Manual com SQLite Direto (`sqlite3` e Data Mappers em código puro)

Consistiria em não utilizar nenhum ORM, escrevendo comandos SQL puros (`SELECT`, `INSERT`, `UPDATE`) e funções manuais de conversão entre tuplas do SQLite e objetos Python.

```python
# DESCARTADO — Exemplo hipotético
def save_barbeiro(conn, barbeiro):
    conn.execute(
        "INSERT OR REPLACE INTO barbeiros (id, nome, inicio, fim) VALUES (?, ?, ?, ?)",
        (barbeiro.id, barbeiro.nome, barbeiro.horario_trabalho.inicio, barbeiro.horario_trabalho.fim)
    )
```

**Por que foi descartado:**
- Embora preservasse a pureza do domínio, exigiria reimplementar manualmente gerenciamento de transações, controle de concorrência, mapeamento de grafos de objetos e identity maps.
- Aumentaria exponencialmente o risco de erros de sintaxe SQL manual e injeção de SQL em rotas mais complexas.
- O SQLAlchemy já fornece uma engine relacional madura e segura; o mapeamento imperativo oferece os benefícios do ORM sem impor a contaminação do modelo.

---

### Alternativa 3 — Serialização em Coluna Única (Document Store / JSON em SQLite)

Consistiria em salvar o agregado inteiro serializado como documento JSON em uma coluna única de texto no SQLite (`id`, `payload_json`), sem mapear colunas relacionais individuais.

**Por que foi descartado:**
- Inviabilizaria consultas relacionais eficientes e filtragens diretas via banco de dados (como `list_by_barbeiro` e constraints de integridade referencial entre `Atendimento` e `Comissao`).
- Perderia as garantias de tipagem e integridade do modelo relacional impostas pelas restrições do projeto.

---

## Consequências

A decisão de adotar o Mapeamento Imperativo acarreta trade-offs específicos que foram avaliados e aceitos pelo time:

---

### Trade-off 1 — Pureza Absoluta e Portabilidade do Domínio vs. Complexidade de Configuração e Boilerplate
- **Ganho:** `src/BarberTime/domain/model.py` permanece um módulo puro em Python, sem uma única linha de código ligada a banco de dados. Os testes unitários das regras de negócio do barbeiro (58 testes no total do projeto) rodam em **0.10s** em memória pura, sem necessidade de banco de dados ativo.
- **Custo correspondente:** A configuração da persistência exige escrever tanto a tabela quanto o mapeador imperativo em `adapters/orm.py`, duplicando a especificação de atributos (ex.: atributo na classe e coluna na `Table`).
- **Por que o trade-off vale:** A velocidade de validação das regras de negócio e a facilidade de refatorar o domínio compensam amplamente as 97 linhas adicionais de configuração em `adapters/orm.py`.

---

### Trade-off 2 — Modelagem Expressiva de Value Objects com `composite()` vs. Conflitos de Nomenclatura no SQLAlchemy 2.0
- **Ganho:** Permite utilizar dataclasses imutáveis ricas (`HorarioTrabalho`, `PercentualComissao`, `ServicoRealizado`) dentro das entidades de domínio, em vez de tipos primitivos espalhados. O ORM reconstitui esses objetos automaticamente ao ler as colunas da tabela.
- **Custo correspondente:** No SQLAlchemy 2.0, o uso de `composite()` é rígido e proíbe que o nome da propriedade mapeada coincida com o nome da coluna física da tabela. Isso exigiu renomeações deliberadas no esquema (como nomear a coluna física de `percentual_valor` para mapear na propriedade `percentual` do composite).
- **Por que o trade-off vale:** A expressividade de ter Value Objects validando suas próprias regras (como o intervalo do percentual de 0 a 100) protege o domínio de inconsistências silenciosas.

---

### Trade-off 3 — Testabilidade Desacoplada vs. Rigidez no Ciclo de Vida Global dos Mappers (`start_mappers`)
- **Ganho:** As suítes de teste de serviços e de domínio não precisam sequer invocar `start_mappers()`, operando exclusivamente com `FakeRepository`s em memória.
- **Custo correspondente:** O mapeamento imperativo registra metadados globalmente no registry do SQLAlchemy. Em testes de integração (`test_repository.py`), é necessário cuidado redobrado para evitar inicializações repetidas de `start_mappers()`, exigindo cláusulas de guarda (`if mapper_registry.mappers: return`) ou fixtures de limpeza.
- **Por que o trade-off vale:** A disciplina na configuração das fixtures é um custo pontual e bem controlado pela equipe em `tests/conftest.py`.

---

## Conclusão

A adoção do **Mapeamento Imperativo (*Classical Mapping*)** com SQLAlchemy 2.0 permitiu ao time BarberTime alcançar o isolamento perfeito preconizado pelo *Ports & Adapters*. 

O domínio — com destaque para as invariantes de expediente do `Barbeiro`, cálculo de `Comissao` e regras de `Fidelidade` — permanece puro, altamente testável e livre de amarras com frameworks de infraestrutura. Os custos de verbosidade e configuração em `adapters/orm.py` foram assimilados como um investimento plenamente compensado pela velocidade, confiabilidade e manutenibilidade do código.
