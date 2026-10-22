# ADR 0001 — Uso do Padrão Repository para Isolar o SQLAlchemy

| Campo | Valor |
|---|---|
| **Status** | Aceita |
| **Data** | 2026-10-22 |
| **Autores** | Time BarberTime |
| **Tema** | Persistência e testabilidade dos agregados |

---

## Contexto

O BarberTime precisa persistir tres agregados principais — `barbeiro`, `Atendimento` e `Comissao` — em um banco de dados relacional (SQLite via SQLAlchemy). O problema central que motivou esta decisão foi a **colisão entre a lógica de negócio e a infraestrutura de persistência**.

Sem uma barreira explícita, o SQLAlchemy tende a "vazar" para dentro das classes de domínio e das rotas Flask de duas formas concretas:

1. **Contaminação do domínio:** as classes `Comissao`, `Atendimento` e `barbeiro` passariam a herdar de `Base` do SQLAlchemy (padrão Active Record declarativo), acoplando objetos de negócio puro a um ORM específico. Qualquer teste unitário que instanciasse um `Comissao`, por exemplo, precisaria de uma sessão de banco ativa — tornando os testes de regra de negócio dependentes de infraestrutura.

2. **Acesso direto à sessão nas rotas:** sem repositórios, os handlers do Flask chamariam `session.query(Comissao).filter_by(...)` diretamente, espalhando SQL por toda a camada HTTP e tornando impossível testar a lógica de negócio (ex.: "não gerar comissão se atendimento não concluído") sem subir um banco de dados.

O agregado `Comissao` ilustra bem o problema: seu construtor em `src/BarberTime/domain/model.py` possui invariantes críticas — `atendimento.concluido` obrigatório e `PercentualComissao` com valor entre 0 e 100 — que precisam ser testadas de forma rápida e isolada. Esse requisito de testabilidade foi o gatilho direto para adotar o padrão Repository.

---

## Decisão

Adotamos o **padrão Repository** (conforme *Architecture Patterns with Python*, Capítulo 2) para toda a camada de persistência do BarberTime.

A implementação em `src/BarberTime/adapters/repository.py` segue a seguinte hierarquia para cada agregado:

```
AbstractXRepository            <- porta (interface ABC pura, sem SQLAlchemy)
    ├── SqlAlchemyXRepository  <- adaptador de produção (usa session)
    └── FakeXRepository        <- adaptador de testes (usa lista em memória)
```

Exemplo concreto para o agregado `Comissao`:

```python
# Porta abstrata — zero imports de SQLAlchemy
class AbstractComissaoRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, comissao: Comissao): ...

    @abc.abstractmethod
    def get(self, comissao_id: int) -> Comissao: ...

    @abc.abstractmethod
    def get_by_atendimento(self, atendimento_id: int) -> Comissao: ...

    @abc.abstractmethod
    def list_by_barbeiro(self, barbeiro_id: int) -> list: ...

# Adaptador de produção — unico arquivo que toca SQLAlchemy
class SqlAlchemyComissaoRepository(AbstractComissaoRepository):
    def __init__(self, session):
        self.session = session

    def get_by_atendimento(self, atendimento_id: int):
        return self.session.query(Comissao).filter_by(
            atendimento_id=atendimento_id
        ).first()
```

O mapeamento entre as classes de domínio e as tabelas é feito **de forma imperativa** em `src/BarberTime/adapters/orm.py` via `mapper_registry.map_imperatively`, garantindo que `Comissao`, `Atendimento` e `barbeiro` **não herdem nenhuma classe do SQLAlchemy** e permaneçam objetos Python puros.

As funções de serviço em `src/BarberTime/service_layer/services.py` recebem os repositórios por **injeção de dependência** (como parâmetros de função), nunca os instanciam internamente — o que permite substituir `SqlAlchemyComissaoRepository` por `FakeComissaoRepository` nos testes sem nenhuma alteração no código de produção.

---

## Alternativas Consideradas

### Alternativa 1 — Active Record declarativo do SQLAlchemy misturado nas rotas Flask

Neste modelo, as classes de domínio herdariam diretamente de `DeclarativeBase` e os handlers Flask acessariam a sessão diretamente:

```python
# DESCARTADO — modelo hipotetico
class Comissao(Base):
    __tablename__ = "comissoes"
    id = Column(Integer, primary_key=True)
    valor = Column(Float)
    # invariantes de negocio ficam fora da classe, nas rotas

@app.route("/comissoes", methods=["POST"])
def post_comissao():
    session = get_session()
    atendimento = session.query(Atendimento).get(data["atendimento_id"])
    if atendimento.status != "Concluido":          # regra de negocio na rota
        return jsonify({"erro": "..."}), 400
    comissao = Comissao(atendimento=atendimento)
    session.add(comissao)
    session.commit()
```

**Por que foi descartado:**
- Todo teste unitário de `Comissao` exigiria uma sessão SQLAlchemy ativa, tornando a suíte lenta e dependente de infraestrutura.
- As invariantes de negócio ficariam espalhadas nas rotas Flask, duplicadas em cada endpoint que cria uma comissão.
- Trocar o ORM exigiria reescrever as classes de domínio inteiras.
- Viola o princípio de inversão de dependências: o domínio passaria a depender da infraestrutura.

---

### Alternativa 2 — Acesso direto à sessão SQLAlchemy dentro da service_layer (sem abstração)

Neste modelo, os serviços importariam e usariam diretamente a sessão, sem interfaces abstratas:

```python
# DESCARTADO — modelo hipotetico
def gerar_comissao(comissao_id, atendimento_id, session):
    atendimento = session.query(Atendimento).filter_by(id=atendimento_id).first()
    comissao = Comissao(id=comissao_id, atendimento=atendimento)
    session.add(comissao)
    session.commit()
```

**Por que foi descartado:**
- A `service_layer` passaria a depender diretamente do SQLAlchemy, violando Ports & Adapters.
- Testar `gerar_comissao` sem banco exigiria mocks complexos da sessão SQLAlchemy (em vez de simplesmente passar um `FakeComissaoRepository`).
- O contrato de persistência — quais operações existem, quais filtros são suportados — ficaria implícito e sem documentação formal.

---

### Alternativa 3 — Repositório generico unico para todos os agregados

Um único `GenericRepository[T]` parametrizado por tipo, compartilhado por todos os agregados.

**Por que foi descartado:**
- Métodos específicos de negócio — `get_by_atendimento` (necessário para garantir "um atendimento só pode ter uma comissão") e `list_by_barbeiro` — não se encaixam em uma interface genérica sem parâmetros opcionais confusos ou castings.
- A interface `AbstractComissaoRepository` documenta explicitamente quais operações o agregado `Comissao` suporta, funcionando como documentação viva do contrato — um repositório genérico perde essa expressividade.

---

## Consequências

As consequências abaixo são organizadas como **pares de trade-off**: cada ganho real traz um custo correspondente que deve ser gerenciado conscientemente.

---

### Trade-off 1 — Testabilidade total vs. Boilerplate triplicado

**Ganho:** `FakeComissaoRepository`, `FakeAtendimentoRepository` e `FakeBarbeiroRepository` permitem que toda a suíte `tests/unit/` rode sem SQLAlchemy, em memória pura, em menos de 2 segundos. A pirâmide de testes fica viável: unitários com Fakes, integração com SQLite em memória (`tests/integration/`), E2E com Flask completo (`tests/e2e/`).

**Custo correspondente:** para cada novo agregado são necessárias 3 classes: 1 interface abstrata + 1 implementação SQLAlchemy + 1 implementação Fake. Com 3 agregados ativos (`barbeiro`, `Atendimento`, `Comissao`), isso já totaliza 9 classes somente em `src/BarberTime/adapters/repository.py`. O boilerplate cresce linearmente com o número de agregados.

**Por que o trade-off vale:** os testes unitários são executados dezenas de vezes por dia durante o desenvolvimento; a velocidade e o isolamento compensam amplamente o custo de escrita do boilerplate inicial.

---

### Trade-off 2 — Domínio livre de infraestrutura vs. Sincronização manual entre Fake e SQLAlchemy

**Ganho:** `src/BarberTime/domain/model.py` não importa Flask, SQLAlchemy ou qualquer biblioteca externa — apenas `dataclasses`, `datetime` e `enum` da stdlib Python. Trocar SQLite por PostgreSQL exige modificar apenas `SqlAlchemy*Repository` e a string de conexão em `flask_app.py`; o domínio e os serviços não mudam.

**Custo correspondente:** se `SqlAlchemyComissaoRepository` ganhar um novo método (ex.: `list_by_periodo`), o `FakeComissaoRepository` precisa ser atualizado manualmente e de forma sincronizada. Um descompasso silencioso entre os dois pode produzir testes que passam com a Fake mas falham em produção — o que é o pior tipo de falso positivo.

**Por que o trade-off vale:** o risco de descompasso é mitigável com testes de integração em `tests/integration/test_comissao_repository.py`, que exercitam `SqlAlchemyComissaoRepository` contra um banco SQLite em memória real, detectando divergências entre as duas implementações.

---

### Trade-off 3 — Contrato explícito por agregado vs. Maior superficie de manutencao

**Ganho:** `AbstractComissaoRepository` documenta formalmente que o agregado `Comissao` suporta `get_by_atendimento` e `list_by_barbeiro`. Essa interface funciona como documentação viva do que é possível fazer com o agregado, tornando o design revisável e comunicável entre os membros do time.

**Custo correspondente:** a separação entre `orm.py`, `repository.py`, `services.py` e `model.py` aumenta o numero de arquivos que um desenvolvedor precisa abrir para entender um único caso de uso de ponta a ponta. O mapeamento imperativo via `mapper_registry.map_imperatively` e o uso de `composite()` para Value Objects (`PercentualComissao`, `ServicoRealizado`) são menos familiares que o modelo declarativo convencional do SQLAlchemy, exigindo curva de aprendizado adicional.

**Por que o trade-off vale:** a divisão explícita de responsabilidades permitiu que os quatro membros do time trabalhassem em paralelo em agregados diferentes (`Barbeiro`, `Atendimento`, `Comissao`, `Fidelidade`) sem conflitos estruturais de merge — benefício diretamente observável no histórico de commits do repositório.

---

> **Conclusão:** A adoção do padrão Repository introduz boilerplate e custo de sincronização, mas esses custos são gerenciáveis e bem delimitados. Em contrapartida, os ganhos em testabilidade — suíte unitária sem banco, pirâmide de testes completa, domínio livre de infraestrutura — são diretos, mensuráveis e alinhados com os critérios de avaliação da disciplina. A decisão permanece válida para o escopo atual do projeto.
