# Análise dos Frameworks — BarberTime

Este documento apresenta a análise técnica crítica dos três principais frameworks adotados no projeto **BarberTime** (**Flask**, **SQLAlchemy** e **pytest**), conforme os requisitos da **Fase 2 — Entrega Final**.

---

## 1. Papel dos Frameworks, Camadas e Independência do Domínio

A tabela abaixo resume o papel de cada framework, a camada arquitetural onde atua no repositório e a garantia de isolamento do domínio de negócio:

| Framework | Papel Principal no BarberTime | Camada Onde Aparece | O Domínio Depende Dele? Por quê? |
|---|---|---|---|
| **Flask** | Microframework web para disponibilização da API REST HTTP. Recebe requisições dos clientes (JSON), delega a execução para a camada de serviços e formata respostas com status codes HTTP apropriados. | `src/BarberTime/entrypoints/` (`flask_app.py`) | **Não.** O módulo de domínio (`domain/model.py`) não possui nenhum `import flask` ou referência a contextos HTTP. Se o Flask fosse substituído por FastAPI, CLI de terminal ou um consumidor de mensagens RabbitMQ, o domínio permaneceria 100% inalterado. |
| **SQLAlchemy** | ORM e toolkit relacional para persistência dos agregados no banco SQLite. Gerencia metadados de tabelas, execução de queries SQL e controle transacional via `Session`. | `src/BarberTime/adapters/` (`orm.py`, `repository.py`) | **Não.** Foi adotado o **mapeamento imperativo clássico** (`map_imperatively`). Nenhuma entidade de negócio herda de classes do ORM (como `DeclarativeBase`). As entidades são objetos Python puros (*POPOs*) que desconhecem a existência de tabelas ou dialetos relacionais. |
| **pytest** | Framework de testes automatizados. Fornece o motor de execução, injeção de dependências por fixtures, suporte a parametrização e relatórios de asserções. | `tests/` (`unit/`, `integration/`, `e2e/`, `conftest.py`) | **Não.** Nenhum arquivo do diretório `src/` importa o `pytest`. O domínio é testado diretamente instanciando objetos normais em memória, sem depender de runners ou classes base de testes. |

### 1.1 O Flask na Borda da Aplicação
O Flask atua estritamente como adaptador primário de entrada (*Driving Adapter*). No arquivo `src/BarberTime/entrypoints/flask_app.py`, os endpoints funcionam como tradutores de protocolos:
```python
# flask_app.py — apenas traduz JSON/HTTP para a chamada de serviço
@app.route("/barbeiros/<int:barbeiro_id>/validar_horario", methods=["POST"])
def validar_horario(barbeiro_id):
    dados = request.get_json() or {}
    try:
        resultado = services.validar_horario_atendimento(
            barbeiro_id=barbeiro_id,
            data_hora=dados.get("data_hora"),
            duracao_minutos=dados.get("duracao_minutos", 0),
            repo=SqlAlchemyBarbeiroRepository(session),
        )
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
```
Essa separação assegura que o núcleo da barbearia permaneça livre de detalhes de serialização web, headers ou cookies.

### 1.2 O SQLAlchemy e o Mapeamento Imperativo
Conforme documentado no [ADR 0002](adr/0002-mapeamento-imperativo-com-sqlalchemy-para-preservar-dominio-puro.md), a opção pelo mapeamento clássico (`mapper_registry.map_imperatively`) em `src/BarberTime/adapters/orm.py` permitiu que a entidade `barbeiro`, o agregado `Comissao` e os objetos de valor `JornadaTrabalho` e `PercentualComissao` fossem modelados com foco exclusivo no negócio:
- A infraestrutura de tabelas (`barbeiros`, `atendimentos`, `comissoes`, `fidelidades`) é configurada de forma dissociada.
- A função `start_mappers()` é o único ponto que conecta tabelas às classes de negócio, preservando a pureza de `domain/model.py`.
- No caso do agregado `Agenda` (`Agendamento`, `RegraDisponibilidade`, `ValidadorHorarioExato` e `ValidadorSuperposicaoHorario`), a independência é total: as regras de conflito de horário operam integralmente em memória no domínio, sem exigir mapeamento em `orm.py`.

### 1.3 O pytest como Ferramenta de Testes Isolados
O `pytest` garante que possamos exercitar tanto a lógica pura de domínio em milissegundos quanto fluxos integrados com SQLite em memória (`conftest.py`). A suíte completa de **129 testes executa em menos de 1 segundo**, sem que o código de produção precise de acoplamento com a biblioteca de asserção.
Na suíte de domínio (`tests/unit/test_domain.py` e `tests/test_gof_agenda_strategy.py`), o `pytest` valida as estratégias de disponibilidade da `Agenda` e o lançamento de `ValueError` via `pytest.raises` sem qualquer fixture de banco de dados.

---

## 2. Inversão de Controle (IoC): Framework vs Biblioteca

### 2.1 A Diferença Fundamental de Conceito
A fronteira entre o uso de uma **biblioteca** e um **framework** é governada pelo **Princípio de Hollywood** (*"Não nos chame, nós chamaremos você"*):
- **Biblioteca:** Nossa aplicação detém o controle do fluxo. Quando precisamos de uma funcionalidade auxiliar (como calcular datas com `datetime` ou fazer hashing com `hashlib`), nosso código chama a biblioteca e o fluxo retorna imediatamente para nós.
- **Framework:** O fluxo de controle é invertido. O framework é o dono da esteira e do loop de execução da aplicação. Ele fornece a arquitetura base e os pontos de extensão (*hooks* ou callbacks) e **ele é quem chama o código da nossa aplicação**.

### 2.2 Pontos Concretos de Inversão de Controle no BarberTime

No BarberTime, identificamos três pontos centrais de IoC:

#### Ponto 1: Roteamento e Despacho de Requisições no Flask
* **Onde ocorre:** Em `src/BarberTime/entrypoints/flask_app.py`, através do decorador `@app.route(...)`.
* **Como funciona a IoC:** Em momento algum da execução do sistema nosso código chama funções como `cadastrar_barbeiro_endpoint()` ou `consultar_barbeiro_endpoint()`. Quem comanda o processo é o servidor WSGI do Flask: ele escuta o socket de rede, recebe a requisição HTTP, faz o parsing dos headers, localiza a função associada na sua árvore interna de rotas e **invoca o nosso endpoint** passando os argumentos da URL. Se a rota não existir, o próprio Flask aborta a requisição com 404 sem consultar nosso código.

#### Ponto 2: Injeção de Dependências e Ciclo de Vida de Fixtures no pytest
* **Onde ocorre:** Em `tests/conftest.py` e `tests/integration/test_repository.py` nas fixtures `@pytest.fixture`.
* **Como funciona a IoC:** Nossos métodos de teste apenas declaram nomes de parâmetros nas assinaturas (ex.: `def test_repositorio_salva_barbeiro(session): ...`). Nós nunca instanciamos a fixture diretamente dentro do teste. O motor do `pytest` analisa os parâmetros por introspecção/reflexão, cria o banco SQLite em memória, abre a `Session`, injeta-a na chamada do teste e, ao término, aciona o bloco `yield` para fechar a conexão (*teardown*). O runner do framework comanda toda a ordem e o ciclo de vida dos testes.

#### Ponto 3: Hidratação e Instanciação de Entidades no SQLAlchemy ORM
* **Onde ocorre:** Em `src/BarberTime/adapters/repository.py`, dentro das chamadas `self.session.query(barbeiro).filter_by(id=barbeiro_id).first()`.
* **Como funciona a IoC:** Quando o repositório consulta o banco, nosso código não cria instâncias de `barbeiro` manualmente com `barbeiro(id=..., nome=...)`. O SQLAlchemy executa o comando SQL, extrai a tupla de dados do banco de dados e **ele próprio instancia o objeto de domínio diretamente em memória**, reconstituindo atributos e objetos de valor mapeados e associando-os ao Identity Map da sessão antes de entregar o objeto pronto ao nosso repositório.

---

## 3. Padrões de Projeto Internos dos Frameworks Localizados no Código

Os frameworks adotados utilizam internamente consagrados padrões de projeto GoF e de arquitetura corporativa (Fowler). Destacamos três deles com base em seu uso concreto no projeto:

### 3.1 Data Mapper (SQLAlchemy)
* **Localização no código:** `src/BarberTime/adapters/orm.py` (função `start_mappers()` e linhas 65-100).
* **Descrição:** O padrão *Data Mapper* (Fowler) estabelece uma camada independente que isola completamente os objetos de negócio em memória do esquema relacional de tabelas. Ao contrário do padrão *Active Record* (onde a entidade herda métodos de persistência como `save()` ou `find()`), o Data Mapper é externo a ambos.
* **Presença no BarberTime:**
  ```python
  # orm.py
  mapper_registry.map_imperatively(
      barbeiro,
      barbeiros,
  )
  ```
  O objeto `mapper_registry` é o Data Mapper em ação: ele conhece a tabela `barbeiros` e a classe pura `barbeiro`, transferindo dados bidirecionalmente sem contaminar a entidade com SQL.

### 3.2 Unit of Work / Identity Map (SQLAlchemy)
* **Localização no código:** `src/BarberTime/service_layer/services.py` e `src/BarberTime/adapters/repository.py`.
* **Descrição:** A `Session` do SQLAlchemy atua como uma *Unit of Work*. Ela mantém um rastreamento contínuo de todas as entidades manipuladas durante uma transação de negócio e registra seu estado no *Identity Map*. Ao final da operação, quando chamamos `session.commit()`, a Unit of Work calcula o menor conjunto de operações SQL necessárias (*dirty checking*) e as aplica atomicamente.
* **Presença no BarberTime:**
  ```python
  # services.py
  def atualizar_expediente(barbeiro_id, novo_inicio, novo_fim, repo, session=None):
      b = repo.get(barbeiro_id) # carregado no Identity Map da sessao
      b.alterar_expediente(novo_inicio, novo_fim) # objeto alterado em memoria
      if session is not None:
          session.commit() # Unit of Work detecta a alteracao e gera UPDATE no SQLite
  ```

### 3.3 Decorator (Flask)
* **Localização no código:** `src/BarberTime/entrypoints/flask_app.py`.
* **Descrição:** O padrão GoF estrutural *Decorator* adiciona responsabilidades a um objeto ou função dinamicamente sem alterar seu código-fonte. O Flask utiliza esse padrão amplamente para o registro declarativo de rotas web.
* **Presença no BarberTime:**
  ```python
  # flask_app.py
  @app.route("/barbeiros", methods=["POST"])
  def cadastrar_barbeiro_endpoint():
      ...
  ```
  O método `@app.route` envolve a função Python pura e a registra na tabela interna de despacho (`url_map`), acoplando regras de método HTTP e parsing sem que a função precise conhecer a infraestrutura interna do servidor.

---

## 4. O que mudaria com um Framework Full-Stack como o Django?

Se o grupo tivesse optado pelo **Django** no início do projeto em vez do combo Flask + SQLAlchemy + pytest, as mudanças no sistema seriam profundas nos âmbitos arquitetural, de modelagem e de testes:

### 4.1 Imposição do Padrão Active Record no Modelo de Domínio
O Django ORM é firmemente baseado no padrão **Active Record**. Todas as entidades precisam obrigatoriamente herdar de `django.db.models.Model`:
```python
# Como ficaria a entidade no Django:
from django.db import models

class Barbeiro(models.Model):
    nome = models.CharField(max_length=255)
    horario_inicio = models.CharField(max_length=5, default="08:00")
    horario_fim = models.CharField(max_length=5, default="18:00")
    dias_trabalho = models.CharField(max_length=50, default="0,1,2,3,4,5")
    # A classe de negocio fica acoplada ao ORM, ao banco e ao runtime do Django
```
**Impactos negativos no BarberTime:**
- **Destruição do Domínio Puro:** Não seria possível manter `domain/model.py` como Python puro. O construtor `__init__` das classes seria sequestrado pelo Django para gerenciar estado de banco de dados.
- **Dificuldade com Value Objects:** O Value Object `JornadaTrabalho` e as estratégias/decoradores da comissão seriam difíceis de mapear, exigindo tabelas adicionais ou bibliotecas de terceiros.
- **Ciclo de vida do Barbeiro (Padrão State):** A implementação elegante da máquina de estados GoF State teria que lidar com campos internos do Django ORM, correndo risco de salvar estados inconsistentes no banco.

### 4.2 Impacto na Testabilidade e Desempenho da Suíte de Testes
- **No BarberTime atual:** A suíte de testes unitários roda em memória pura sem banco de dados em **menos de 1 segundo**.
- **Com Django:** O test runner padrão do Django cria e destrói um banco de dados real a cada rodada de testes para rodar as migrações. Mesmo testes que apenas verificam se um barbeiro aceita um horário passariam a depender do setup do Django, aumentando o tempo de execução de segundos para dezenas de segundos ou minutos.

### 4.3 Produtividade vs Arquitetura Orientada a Domínio (*The Django Way*)
- **O que ganharíamos:** Painel administrativo completo pronto (`django-admin`), sistema de autenticação de usuários nativo, migrações automáticas maduras (`makemigrations`) e proteção contra ataques web (CSRF, XSS) habilitada por padrão.
- **O que perderíamos:** A liberdade de desenhar uma arquitetura limpa em camadas (*Ports & Adapters*). No Django, a convenção padrão empurra todo o código para dentro de `views.py` e `models.py` (*fat models, fat views*), lutando ativamente contra a criação de Repositórios e Camadas de Serviço independentes.

**Conclusão da Comparação:**  
Para um CRUD corporativo simples de curto prazo, o Django traria telas e formulários mais rápido. Porém, para os objetivos da disciplina — aplicar DDD, isolamento de camadas arquiteturais, refatorações SOLID e padrões GoF no domínio —, o conjunto **Flask + SQLAlchemy Imperativo** mostrou-se incomparavelmente superior para preservar o controle do desenvolvedor sobre a arquitetura.
