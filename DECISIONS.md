# BarberTime - Registro de Decisões de Arquitetura (DECISIONS.md)

## Fase 1 (Semanas 1 a 4)

### Integrante: Jonathan do Nascimento Melo (`JonathanMelo0`)
**Agregado sob minha responsabilidade:** Barbeiro

---

#### Semana 1 — Proposta de Domínio e Divisão de Tarefas
- **O que eu fiz:** Na divisão do grupo, fiquei responsável pelo agregado do **Barbeiro**. Ajudei a fechar a proposta do sistema de barbearia no `PROPOSTA.md` e montei a tabela de divisão de responsabilidades no `README.md`. Também adicionei as bibliotecas que a gente ia precisar no `requirements.txt` (`pytest`, `SQLAlchemy`, `Flask`) e deixei o `pytest.ini` configurado para não dar erro de import no terminal.
- **Arquivos:** `PROPOSTA.md`, `README.md`, `requirements.txt`, `pytest.ini`.
- **Commits:** `b40e6f8` e commits de configuração e README.
- **Justificativa da decisão de projeto:** Escolhi separar o Barbeiro como um agregado próprio para que a regra de horário de trabalho ficasse concentrada nele. Dessa forma, a validação de expediente não fica misturada com a criação de agendamentos da Agenda nem com o cadastro solto de clientes.

---

#### Semana 2 (Checkpoint 1) — Modelo de Domínio e Invariantes
- **O que eu fiz:**
  - Implementei a classe `barbeiro` no `src/BarberTime/domain/model.py` como a raiz do agregado, protegendo a invariante principal: **"Impedir agendamentos fora do horário de trabalho"**.
  - Defini que cada barbeiro tem seu horário de início, fim de expediente (por padrão das 08:00 às 18:00) e os dias da semana que atende.
  - Criei métodos no modelo como `pode_atender()`, `validar_agendamento()`, `adicionar_agendamento()` e `alterar_expediente()`, além do objeto de valor `HorarioTrabalho`.
  - Tomei o cuidado de manter o `__init__` compatível com o que o Marcello já tinha instanciado no teste dele (`barbeiro(id=10, nome="Junior")`), para não quebrar o código de ninguém.
  - Implementei igualdade por identidade (`__eq__` e `__hash__` usando o `id`), que é o padrão de entidades no livro.
  - Escrevi 12 testes unitários em `tests/unit/test_barbeiro.py` testando todos os casos: agendamento normal, tentativa antes do início, tentativa após o fim, serviço com duração que passa do horário de fechamento, agendamento em dia de folga e troca de expediente.
- **Arquivos:** `src/BarberTime/domain/model.py`, `tests/unit/test_barbeiro.py`.
- **Commits:** commits do modelo do barbeiro e testes unitários.
- **Justificativa da decisão de projeto:** Deixei o arquivo `model.py` totalmente puro, sem importar nada de banco ou Flask. Decidi fazer a validação da duração do corte dentro do barbeiro porque se o barbeiro fecha às 18h e o cliente tenta marcar um corte de 30 min às 17h45, o atendimento passaria do expediente (iria até 18h15), então a própria entidade já rejeita com erro.

---

#### Semana 3 (Checkpoint 2) — Repositórios e Mapeamento ORM
- **O que eu fiz:**
  - Criei a interface abstrata `AbstractBarbeiroRepository` em `src/BarberTime/adapters/repository.py` herdando de `AbstractRepository`, com os métodos `add`, `get` e `list`.
  - Implementei o repositório real `SqlAlchemyBarbeiroRepository` usando a `Session` do SQLAlchemy para salvar e buscar barbeiros no banco SQLite.
  - Criei também o `FakeBarbeiroRepository` em memória (guardando os objetos em lista), que serve para testar as camadas superiores rápido, sem precisar abrir conexão de banco de dados.
  - Em `src/BarberTime/adapters/orm.py`, fiz o mapeamento imperativo (`mapper_registry.map_imperatively`) ligando a tabela `barbeiros` à classe `barbeiro`, seguindo o estilo do Capítulo 2 do livro do curso.
  - Em `tests/integration/test_repository.py` e `tests/conftest.py`, criei testes de integração com SQLite em memória para garantir que o barbeiro é salvo e recuperado do banco com todos os campos preservados.
- **Arquivos:** `src/BarberTime/adapters/repository.py`, `src/BarberTime/adapters/orm.py`, `tests/integration/test_repository.py`, `tests/conftest.py`.
- **Commits:** commits de repositório, ORM, fixtures e testes de integração.
- **Justificativa da decisão de projeto:** Optei pelo mapeamento imperativo clássico do SQLAlchemy em vez de usar `declarative_base` com classes herdadas do ORM. Assim a classe `barbeiro` continua sendo um objeto Python comum do domínio, sem depender do banco. O Fake Repository me permitiu depois testar a camada de serviços de forma muito mais simples.

---

#### Semana 4 (Fase 1 Entrega) — Camada de Serviço e Endpoints Flask
- **O que eu fiz:**
  - Em `src/BarberTime/service_layer/services.py`, implementei os casos de uso para o meu agregado: `cadastrar_barbeiro`, `consultar_barbeiro`, `listar_barbeiros`, `atualizar_expediente` e `validar_horario_atendimento`.
  - Criei testes unitários para a camada de serviços em `tests/unit/test_services.py` usando o `FakeBarbeiroRepository`.
  - Em `src/BarberTime/entrypoints/flask_app.py`, criei as rotas da API:
    - `POST /barbeiros`: cadastra um barbeiro (retorna 201).
    - `GET /barbeiros`: lista todos os barbeiros (retorna 200).
    - `GET /barbeiros/<id>`: busca um barbeiro específico (200 ou 404 se não achar).
    - `PUT /barbeiros/<id>/expediente`: altera o horário de início/fim (retorna 200).
    - `POST /barbeiros/<id>/validar_horario`: rota que o front-end ou outro serviço pode chamar para checar se o barbeiro está livre/disponível naquele horário antes de agendar (retorna 200 se der certo ou 400 se for fora do horário).
  - Em `tests/e2e/test_api.py`, fiz testes de ponta a ponta chamando o client de teste do Flask para garantir que os retornos JSON e códigos de status HTTP estão corretos.
- **Arquivos:** `src/BarberTime/service_layer/services.py`, `src/BarberTime/entrypoints/flask_app.py`, `tests/unit/test_services.py`, `tests/e2e/test_api.py`.
- **Commits:** commits de serviços, testes com fake repo, rotas Flask e testes de API.
- **Justificativa da decisão de projeto:** A camada de serviço cuida da orquestração e da transação (commit no banco), deixando a rota do Flask apenas com o papel de receber o JSON da requisição e devolver a resposta HTTP com o status code correto (201 para criação, 400 para dados inválidos ou horário fora do expediente, 404 para id não encontrado).

---

#### Declaração de Uso de IA e Simplificações
- **Uso de IA:** Conforme as regras da Seção 2.5, usei assistente de IA exclusivamente para tirar dúvidas conceituais sobre como funcionava a sintaxe do `map_imperatively` no SQLAlchemy 2.0 (já que a versão mais nova mudou um pouco em relação a versões antigas da documentação) e para conferir a estrutura recomendada de pastas do Apêndice B. Todo o fluxo, regras de negócio do barbeiro e testes foram planejados e implementados para o nosso domínio.
- **Simplificações conscientes:** Para guardar os dias trabalhados na semana nesta Fase 1, usei uma representação de números separados por vírgula (`"0,1,2,3,4,5"` onde 0 é segunda e 6 é domingo) gravada em coluna simples de texto no SQLite. Isso resolveu perfeitamente a regra de folga sem precisar criar uma tabela associativa a mais nesta primeira fase.
