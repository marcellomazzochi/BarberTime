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

---

### Integrante: Ruan do Nascimento Silva (`ruanlov`)
**Agregado sob minha responsabilidade:** Comissão

---

#### Semana 1 — Proposta de Domínio e Divisão de Tarefas
- **O que eu fiz:** Na divisão do grupo, fiquei responsável pelo agregado da **Comissão**, cuja invariante é **"Impedir geração de comissão para o barbeiro de atendimentos que não estejam concluídos"**. Participei da definição do domínio da barbearia no `PROPOSTA.md` e da tabela de divisão de responsabilidades no `README.md`. Segui o mesmo desenho de pastas e o mesmo `pytest.ini` que o Jonathan já havia configurado, para não criar um padrão paralelo.
- **Arquivos:** `PROPOSTA.md`, `README.md`.
- **Justificativa da decisão de projeto:** Escolhi manter o Comissão como um agregado separado do Barbeiro e da Agenda. Assim a regra "só gera comissão de atendimento concluído" fica concentrada na raiz do meu agregado, e não espalhada pelo fluxo de agendamento do Marcello nem pelo cadastro de barbeiros do Jonathan.

---

#### Semana 2 (Checkpoint 1) — Modelo de Domínio e Invariantes
- **O que eu fiz:**
  - Estendi o `src/BarberTime/domain/model.py` com a entidade `Atendimento` (id, barbeiro, serviço, data/hora e status) e o agregado `Comissao` (id, atendimento, barbeiro, percentual e valor).
  - Modelei o ciclo de vida do atendimento com o enum `StatusAtendimento` (`AGENDADO`, `CONCLUIDO`, `CANCELADO`, `FALTOU`) e métodos `concluir()`, `cancelar()`, `marcar_falta()` e a propriedade `concluido`/`pode_gerar_comissao()`.
  - Coloquei a invariante principal no construtor do `Comissao`: se o `atendimento` não estiver com status `CONCLUIDO`, o objeto nem pode ser criado (`ValueError`). Também valido que o atendimento pertence ao barbeiro informado.
  - Criei dois objetos de valor: `PercentualComissao` (valida o intervalo maior que 0 e menor/igual a 100 e sabe aplicar sobre o preço) e `ServicoRealizado` (snapshot de nome, duração e preço do serviço no momento do atendimento), além de reutilizar a ideia do objeto `preco`.
  - Mantive igualdade por identidade (`__eq__`/`__hash__` pelo `id`) em `Atendimento` e `Comissao`, igual ao padrão que o Jonathan usou no `barbeiro`.
  - Escrevi 16 testes unitários em `tests/unit/test_comissao.py` cobrindo: tentativa de gerar comissão com atendimento agendado, cancelado e com falta (todos rejeitados), geração com atendimento concluído, percentual padrão de 10% e percentual customizado, percentual inválido, atendimento de outro barbeiro, transições de status inválidas e igualdade por identidade.
- **Arquivos:** `src/BarberTime/domain/model.py`, `tests/unit/test_comissao.py`.
- **Justificativa da decisão de projeto:** Deixei o `model.py` puro de propósito, sem importar Flask ou banco. A validação no construtor do agregado garante que seja impossível existir uma `Comissao` apontando para atendimento não concluído, mesmo que alguém tente criar o objeto direto, sem passar pela camada de serviço. O `ServicoRealizado` como value object evita que a comissão dependa de uma entidade `servico` mutável e preserva o preço praticado na data do atendimento.

---

#### Semana 3 (Checkpoint 2) — Repositórios e Mapeamento ORM
- **O que eu fiz:**
  - Em `src/BarberTime/adapters/repository.py`, criei as interfaces `AbstractAtendimentoRepository` e `AbstractComissaoRepository` (herdando de `AbstractRepository`), seguindo exatamente o padrão do `AbstractBarbeiroRepository` do Jonathan.
  - Implementei os repositórios reais `SqlAlchemyAtendimentoRepository` e `SqlAlchemyComissaoRepository`, além dos `FakeAtendimentoRepository` e `FakeComissaoRepository` em memória para os testes rápidos de serviço. No repositório de comissão incluí `get_by_atendimento()` e `list_by_barbeiro()`.
  - Em `src/BarberTime/adapters/orm.py`, criei as tabelas `atendimentos` e `comissoes` e os mapeamentos imperativos (`map_imperatively`). Usei `relationship` para ligar à tabela `barbeiros` já existente e `composite` para mapear os value objects `ServicoRealizado` e `PercentualComissao` em colunas.
  - Em `tests/integration/test_comissao_repository.py`, fiz testes de integração com SQLite em memória verificando a gravação/leitura do atendimento e da comissão, incluindo as colunas cruas via SQL e o filtro de comissões por barbeiro.
- **Arquivos:** `src/BarberTime/adapters/repository.py`, `src/BarberTime/adapters/orm.py`, `tests/integration/test_comissao_repository.py`.
- **Justificativa da decisão de projeto:** Segui o mapeamento imperativo clássico do livro para as classes de domínio continuarem sendo Python puro. No `composite` do percentual, tive que usar uma coluna física com nome diferente (`percentual_valor`), porque o SQLAlchemy não deixa o nome da coluna conflitar com o nome da propriedade mapeada. Preferi gravar o preço do serviço como snapshot (`servico_preco`, `servico_nome`, `servico_duracao`) em vez de amarrar a comissão a uma tabela de serviços, porque a comissão tem que refletir o valor praticado na data do atendimento.

---

#### Semana 4 (Fase 1 Entrega) — Camada de Serviço e Endpoints Flask
- **O que eu fiz:**
  - Em `src/BarberTime/service_layer/services.py`, implementei os casos de uso do meu agregado: `registrar_atendimento`, `concluir_atendimento`, `consultar_atendimento`, `gerar_comissao`, `consultar_comissao`, `listar_comissoes` e `listar_comissoes_por_barbeiro`.
  - O `gerar_comissao` verifica se o atendimento existe, se ainda não há comissão gerada para ele e delega a validação da invariante para a própria entidade `Comissao`; o `commit` da transação fica na camada de serviço, como no restante do projeto.
  - Escrevi 12 testes unitários de serviço em `tests/unit/test_services_comissao.py` usando os fakes, cobrindo o bloqueio da comissão de atendimento não concluído, o fluxo `registrar -> concluir -> gerar`, percentual customizado, comissão duplicada e listagem por barbeiro.
  - Em `src/BarberTime/entrypoints/flask_app.py`, adicionei as rotas:
    - `POST /atendimentos`: registra um atendimento (retorna 201).
    - `GET /atendimentos/<id>`: consulta um atendimento (200 ou 404).
    - `POST /atendimentos/<id>/concluir`: conclui o atendimento (retorna 200).
    - `POST /comissoes`: gera a comissão (201 ou 400 se o atendimento não estiver concluído, não pertencer ao barbeiro, percentual inválido ou já existir comissão).
    - `GET /comissoes` e `GET /comissoes/<id>`: listam e consultam comissões.
    - `GET /barbeiros/<id>/comissoes`: lista as comissões de um barbeiro.
  - Em `tests/e2e/test_api_comissao.py`, escrevi testes de ponta a ponta com o client de teste do Flask confirmando o retorno 400 ao tentar gerar comissão de atendimento agendado e o retorno 201 (valor calculado) após concluir.
- **Arquivos:** `src/BarberTime/service_layer/services.py`, `src/BarberTime/entrypoints/flask_app.py`, `tests/unit/test_services_comissao.py`, `tests/e2e/test_api_comissao.py`.
- **Commits:** commits de modelo/agregado, repositórios e ORM, serviços, rotas Flask e testes (unitários, integração e e2e).
- **Justificativa da decisão de projeto:** A rota do Flask só recebe o JSON, monta o dicionário de serviço e devolve o status HTTP correto; toda a regra de negócio fica no domínio e a orquestração na camada de serviço. A resposta 400 com a mensagem "Nao e possivel gerar comissao para atendimento nao concluido" deixa explícito para o front-end por que a comissão não foi criada.

---

#### Fase 1

#### Integrante: Marcello Bimbatti Mazzochi (`marcellomazzochi`)
**Agregado sob minha responsabilidade:** Agenda

---

**O que eu fiz:**
- Idealizei o modelo de negócio do projeto e montei a estrutura obrigatória do repositório.
- Modelei a primeira versão das entidades e objeto de valor das classes: `cliente`, `servico`, `barbeiro`, `preco`, `Agendamento` e o agregado `Agenda`.
- No agregado `Agenda` garanti o bloqueio na marcação de horários duplicados para o mesmo barbeiro com o método `adicionar_agendamento`.
- Escrevi testes unitários (`test_domain.py`) para agendamento e validação do bloqueio para horários conflitantes.
- Configurei o arquivo .github/workflows/ci.yml
  
**Arquivos:** `src/BarberTime/domain/model.py`, `tests/unit/test_domain.py`, `.github/workflows/ci.yml`.

**Commits:**
b1773de update ci.yml,
cd598c6 Update CI,
97a30b0 Add pythonpath,
f2236bb Add ci.yml,
3a7ad95 (tag: fase1-checkpoint-1) Add teste agendar mesmo horario,
3b45796 add agendar_mesmo_horario,
caf9c53 Funcao agendar mesmo horario,
ea737f6 Add objeto de valor preco,
9827d16 add AbstractRepository,
bb1c5c3 add import abc,
bcaabb6 update test_domain.py,
53747a1 update test_domain.py,
cf5d00c update agendamento,
2d05a1f update test_domain.py,

**Uso de IA Generativa :**
- Utilizei IA para configuração do arquivo `.github/workflows/ci.yml` do GitHub Actions e para entender a arquitetura exigida no projeto.

**Justificativa da decisão de projeto:** 
- O tema do projeto foi escolhido pensando em uma aplicação que pudesse ser demandada em um ambiente corporativo.
- A classe `Agenda` tem o dicionário `agendamentos` com a chave: `barbeiro, data_hora, que garante o modelo de negócio que proíbe sobreposições de horários com o mesmo barbeiro.


### Integrante: Johnny de Godoy (`johnn2c`)
**Agregado sob minha responsabilidade:** Fidelidade

---

#### Fase 1 — Proposta inicial

**Data registrada:** 27/09/2026  
**Período estimado de elaboração:** semana de 21 a 27/09/2026.

**O que eu fiz:**

Participei da elaboração e atualização da proposta inicial do projeto BarberTime, contribuindo para a definição do sistema e das funcionalidades previstas para a aplicação.

**Arquivo alterado:**
- `PROPOSTA.md`

**Commit:**
- `e7d3178` — Update PROPOSTA.md

**Decisão de projeto:**

A proposta inicial foi desenvolvida considerando a necessidade de um sistema de gerenciamento de barbearia que contemplasse diferentes responsabilidades do negócio, incluindo o controle de clientes, agendamentos, atendimentos, comissões e fidelização.

---

#### Fase 1 — Checkpoint 2: Implementação do Agregado Fidelidade

**Responsabilidade:** Desenvolvimento do agregado `Fidelidade`, incluindo regras de domínio, testes, persistência, repositórios, serviços e endpoints da API.

**O que eu fiz:**

Fiquei responsável pelo desenvolvimento do agregado Fidelidade, implementando as funcionalidades relacionadas ao programa de benefícios dos clientes da barbearia.

Inicialmente, desenvolvi e ajustei a entidade `Fidelidade`, concentrando nela as regras de negócio responsáveis pelo controle dos cortes realizados e pela disponibilização de benefícios gratuitos.

Durante a implementação, também desenvolvi os mecanismos necessários para impedir o resgate de benefícios quando existe um registro de no-show, garantindo que essa restrição fosse validada pela própria entidade.

As principais atividades realizadas foram:

- Criação e implementação do agregado `Fidelidade` no modelo de domínio.
- Desenvolvimento de testes unitários para validar as regras de negócio e o comportamento da entidade.
- Refatoração dos testes de fidelidade para melhorar a organização e compatibilidade com o restante do projeto.
- Criação da tabela de fidelidade no banco de dados SQLite.
- Implementação dos repositórios abstrato, SQLAlchemy e Fake para acesso e persistência dos dados.
- Desenvolvimento das funções de serviço responsáveis pelo cadastro, consulta, listagem, registro de cortes, registro de no-show e resgate de benefícios.
- Implementação do método `registrar_no_show()` na entidade `Fidelidade`.
- Desenvolvimento de teste de integração para verificar a interação entre o agregado e a persistência.
- Criação dos endpoints Flask para disponibilizar as operações de fidelidade por meio da API.
- Realização de ajustes para compatibilizar a implementação com os testes e a arquitetura existente.

**Arquivos relacionados:**

| Arquivo | Responsabilidade |
|---|---|
| `src/BarberTime/domain/model.py` | Implementação das regras de negócio do agregado Fidelidade. |
| `src/BarberTime/adapters/orm.py` | Criação da tabela e mapeamento ORM da fidelidade. |
| `src/BarberTime/adapters/repository.py` | Implementação dos repositórios de fidelidade. |
| `src/BarberTime/service_layer/services.py` | Implementação dos casos de uso e operações de fidelidade. |
| `src/BarberTime/entrypoints/flask_app.py` | Disponibilização das operações por meio de endpoints Flask. |
| `tests/unit/test_fidelidade.py` | Testes unitários das regras de negócio. |
| `tests/integration/test_fidelidade_repository.py` | Teste de integração da persistência. |

**Commits relacionados:**

| Hash | Descrição |
|---|---|
| `a3a3e42` | Adicionado agregado de fidelidade. |
| `154a7a5` | Criação dos testes unitários de fidelidade. |
| `f8e6176` | Ajustes no agregado de fidelidade. |
| `5a0074a` | Ajustes para atendimento aos testes de fidelidade. |
| `cb59b47` | Adicionada tabela de fidelidade. |
| `197742` | Adicionados repositórios de fidelidade. |
| `fe6fca` | Adicionado teste de integração. |
| `448f543` | Adicionado registro de no-show na classe Fidelidade. |
| `4d13e7f` | Adicionadas funções de fidelidade na camada de serviços. |
| `63f4de8` | Adicionadas rotas de fidelidade. |

**Decisão técnica:**

A implementação do agregado Fidelidade foi organizada seguindo a separação de responsabilidades da arquitetura em camadas. As regras de negócio foram mantidas na entidade de domínio, enquanto a persistência ficou sob responsabilidade dos repositórios, a orquestração dos casos de uso na camada de serviços e a comunicação externa nos endpoints Flask.

A principal decisão foi manter a validação do no-show dentro do próprio agregado, evitando que a regra de bloqueio do benefício dependesse exclusivamente da camada de API. Dessa forma, qualquer operação de resgate precisa respeitar a invariante definida no domínio.

**Declaração de Uso de IA:**

Utilizei ferramentas de IA generativa como apoio durante o desenvolvimento, principalmente para esclarecer dúvidas de implementação, revisar a organização dos testes e auxiliar na compatibilização do agregado com a arquitetura existente. As sugestões foram utilizadas como suporte ao desenvolvimento e ajustadas conforme as necessidades do projeto.

---

## Parte 2 — Fase 2

### Ruan do Nascimento Silva - Checkpoint 1

**O que fiz e arquivos modificados:**
Fiquei responsável pela estruturação inicial da documentação arquitetural. Escrevi as seções de Escopo, Requisitos Arquiteturais (em formato de cenários) e a Arquitetura Atual com o diagrama Mermaid no arquivo `docs/arquitetura.md`. Também redigi o meu ADR pessoal focado no isolamento do banco de dados no arquivo `docs/adr/0001-uso-do-padrao-repository-para-isolar-sqlalchemy.md`.

**Commits:**
- `5dffab1dc6e57ecc480ea199a1dab8a5334206c7` - docs: adiciona escopo, requisitos e diagrama da arquitetura atual.
- `ac69c3a2fdcf61ce2e2d5134dcb510673f91eb29` - docs: adiciona ADR sobre a utilizacao do padrao Repository.

**Decisão de projeto:**
Decidi documentar a adoção do padrão Repository no BarberTime porque centralizar o acesso aos dados nos permite testar a lógica de cálculo de comissões mais rapidamente em memória, sem depender do banco de dados real.

**Uso de IA:**
Utilizei o LLM Antigravity para me auxiliar na estruturação e formatação inicial dos arquivos Markdown. Forneci o código atual do nosso repositório como contexto e pedi que a IA gerasse os rascunhos do diagrama Mermaid e do texto base do ADR seguindo rigorosamente as restrições da disciplina, como os cenários mensuráveis e a estrutura de trade-offs. Todo o conteúdo retornado foi revisado, validado e ajustado por mim para refletir as decisões reais do projeto.

---

### Jonathan do Nascimento Melo (`JonathanMelo0`) — Checkpoint 1

**O que fiz e arquivos modificados:**
- Fiquei responsável por redigir a análise de trade-offs (Seção 4) e levantar as evidências reais (Seção 6) no `docs/arquitetura.md`, além de escrever o meu ADR em `docs/adr/0002-mapeamento-imperativo-com-sqlalchemy-para-preservar-dominio-puro.md`.
- Na análise de trade-offs, avaliei como a arquitetura atual (Ports & Adapters, Service Layer e Mapeamento Imperativo) afeta a manutenibilidade, testabilidade e desempenho. Destaquei os trade-offs práticos que enfrentamos, como a alta testabilidade que exigiu criar classes Fake para cada repositório, e os riscos de concorrência com locks de arquivo no SQLite sob acessos concorrentes.
- Na parte de evidências, levantei dados reais da execução do pytest mostrando a velocidade da suíte unitária (58 testes em 0.10s) contra os testes com banco/Flask (0.65s), a adição modular do agregado Comissão sem quebrar o código anterior, e a proporção de linhas de persistência comparadas ao domínio.
- Escrevi o ADR 0002 registrando a decisão que tomei no agregado do Barbeiro de usar o Classical Mapping (`map_imperatively`) com `composite` para os Value Objects de horário, explicando o contexto e as alternativas descartadas.

**Arquivos:**
- `docs/arquitetura.md`
- `docs/adr/0002-mapeamento-imperativo-com-sqlalchemy-para-preservar-dominio-puro.md`
- `DECISIONS.md`

**Commits:**
- Commits de trade-offs e evidências em `docs/arquitetura.md` (`f478be6`) e do ADR 0002 (`faeafa3`).

**Decisão de projeto:**
Decidi documentar a adoção do mapeamento imperativo (`map_imperatively`) no ADR 0002 porque essa foi a decisão técnica que permitiu manter o Barbeiro e o HorarioTrabalho como classes Python puras, validando expediente e horários sem nenhuma amarra com o SQLAlchemy ou banco de dados.

**Uso de IA:**
Usei IA pontualmente para tirar dúvidas sobre a formatação dos cenários de atributos de qualidade em Markdown e revisar a concordância dos textos de trade-offs e do ADR. Todo o raciocínio, dados da suíte de testes e argumentos técnicos foram feitos com base no código do nosso projeto.

---

### Marcello Bimbatti Mazzochi (`marcellomazzochi`) — Fase 2 Checkpoint 1

**O que fiz e arquivos:**
Documentei a decisão do agregado Agenda em ADR 0003 e atualizei o diagrama da arquitetura para mostrar a Agenda e seus testes.
- `docs/adr/0003-agenda-impede-conflitos-de-horario.md`
- `docs/arquitetura.md`

**Commits:** 
927e12ebc13940fc147e5f2fe98a6db7a23f0a7e e 353c95a2f4cd6a80d1c764e496958eb995b968ba - Criação ADR 0003
ddde18bfe187b59e3053b037e679e1d2974be0e4 - Update arquivo arquitetura

**Decisão de projeto:**
Mantive no diagrama a Agenda como parte do domínio, sem ligar no repositório ou banco, porque a implementação atual guarda os agendamentos em memória.

**Uso de IA:**
Usei IA para consultar o código dos colegas, levantar os pontos importantes para o ADR e ajustar o diagrama em `arquitetura.md`


---
## Parte 2 — Fase 2

### Integrante: Johnny de Godoy (`johnn2c`) — Checkpoint 1

**Responsabilidade:** Análise arquitetural comparativa e documentação da decisão relacionada ao isolamento dos testes unitários.

**O que fiz e arquivos modificados:**

Fiquei responsável por complementar a documentação arquitetural do projeto, contribuindo com a análise das alternativas de arquitetura e com o registro de decisões técnicas.

Minhas atividades foram:

- Atualizei o arquivo `docs/arquitetura.md`, adicionando a Seção 5, dedicada à análise comparativa entre a arquitetura atual do BarberTime e a alternativa Active Record + Transaction Script.
- Analisei as diferenças entre as duas abordagens considerando os atributos de qualidade de manutenibilidade, testabilidade e desempenho.
- Avaliei os benefícios e limitações da arquitetura atual, baseada em Ports & Adapters, Repository e Service Layer.
- Registrei os motivos para manter a arquitetura adotada no projeto, considerando a separação de responsabilidades e a facilidade de testar as regras de negócio independentemente da infraestrutura.
- Elaborei um ADR para documentar a decisão arquitetural relacionada ao isolamento dos testes unitários.
- Realizei ajustes no identificador do ADR para manter a sequência e a organização dos documentos de decisões arquiteturais do projeto.

**Arquivos relacionados:**

| Arquivo | O que foi realizado |
|---|---|
| `docs/arquitetura.md` | Adição da análise comparativa entre as arquiteturas e avaliação dos atributos de qualidade. |
| `docs/adr/` | Criação e atualização do identificador do ADR relacionado ao isolamento dos testes unitários. |

**Commits:**

| Hash | Descrição |
|---|---|
| `f6cfde` | Adicionada Seção 5 da documentação arquitetural. |
| `64ca6bb` | Atualização do arquivo de arquitetura. |
| `54b2ac6` | Adicionado ADR de isolamento dos testes unitários. |
| `7c30b43` | Alterado identificador do ADR. |

**Decisão de projeto:**

A análise comparativa demonstrou que a arquitetura atual, baseada em Ports & Adapters, Repository e Service Layer, oferece uma separação de responsabilidades que favorece a manutenibilidade e a testabilidade do sistema.

A alternativa Active Record + Transaction Script foi considerada, mas não foi adotada, pois concentraria responsabilidades de persistência e regras de negócio em estruturas mais acopladas. A decisão foi manter a arquitetura existente, preservando o domínio independente da infraestrutura e permitindo testar as regras de negócio utilizando repositórios Fake.

Também documentei a importância do isolamento dos testes unitários, permitindo validar o comportamento das entidades e dos serviços sem depender de conexões com o banco de dados ou de componentes externos.

**Declaração de Uso de IA:**

Utilizei o ChatGPT como ferramenta de apoio para compreender os requisitos da atividade e analisar as diferenças entre as alternativas arquiteturais. As sugestões foram utilizadas como auxílio, sendo ajustadas de acordo com a arquitetura e as características reais do projeto.

---
### Observação sobre o histórico

As datas foram organizadas a partir do histórico de commits disponível. Os períodos identificados como estimados representam aproximações do período de trabalho, e não necessariamente o horário ou o dia em que cada atividade foi iniciada.



---

## Fase 2 — Checkpoint 2 (Semana de SOLID)

### Integrante: Ruan do Nascimento Silva (`ruanlov`)
**Agregado sob minha responsabilidade:** Comissão

---

#### Checkpoint 2 — Parte 2: Refatoração SOLID no Agregado de Comissão

**Arquivos alterados:**

| Arquivo | Tipo de alteração |
|---|---|
| `src/BarberTime/domain/model.py` | Adição de `EstrategiaComissao` (ABC) e três implementações concretas (`ComissaoPercentualFixo`, `ComissaoBarbeiroSenior`, `ComissaoBarbeiroJunior`); refatoração do construtor de `Comissao` para injetar a estratégia. |
| `src/BarberTime/service_layer/services.py` | Adição do parâmetro opcional `estrategia: EstrategiaComissao` em `gerar_comissao`; ajuste de `_comissao_para_dict` para serializar `percentual=None`. |
| `tests/unit/test_comissao.py` | 11 novos testes das estratégias (isolados) + 16 testes originais preservados = 27 testes. |
| `tests/unit/test_services_comissao.py` | 4 novos testes do fluxo de serviço com estratégias + 12 originais preservados = 16 testes. |
| `docs/solid.md` | Documento de análise SOLID com a violação identificada, o problema concreto, a refatoração e os trade-offs. |

**Decisão técnica (uma frase):**
Apliquei o **padrão Strategy** (OCP) ao cálculo de comissão introduzindo a hierarquia `EstrategiaComissao` para que novas políticas de repasse — como os 15% para barbeiros sênior ou o desconto de R$ 5,00 de insumos para juniores — possam ser adicionadas criando-se apenas uma nova subclasse, sem abrir nem modificar a classe `Comissao` ou a função `gerar_comissao`.

**Hashes de commit:**

| Marco | Hash abreviado |
|---|---|
| Último commit antes da refatoração (`350a58b`) | `350a58b` |
| Commit que introduz a refatoração (OCP com Strategy) | `84dd28c` |
| Commit de documentação (`docs/solid.md` + este DECISIONS.md) | `85bd126` |

**Declaração de Uso de IA:**
Utilizei o agente **Antigravity (Claude Sonnet 4.6 / Gemini 3.8 Flash)** para automatizar integralmente esta refatoração: o agente explorou de forma autônoma o repositório BarberTime, identificou a violação do OCP no agregado de Comissão, escolheu o padrão Strategy como solução, escreveu o código refatorado em `model.py` e `services.py`, adicionou 15 novos testes (mantendo os 28 originais verdes) e redigiu a seção `docs/solid.md` com análise, trade-offs e marcadores de hash. Todo o conteúdo foi revisado e validado por mim antes de ser incorporado ao repositório.

---

### Integrante: Marcello Bimbatti Mazzochi (`marcellomazzochi`)
**Agregado sob minha responsabilidade:** Agenda

---

#### Checkpoint 2 — Parte 2: Refatoração SOLID no Agregado de Comissão

* **O que fiz:** Refatorei a classe `Agenda` no arquivo `src/BarberTime/domain/model.py` para adequação aos princípios OCP, delegando a lógica de validação de horário. Adicionei a documentação da refatoração no `docs/solid.md`.
* **Commits:** `9e4fea2911b43eeda771d4ba603be05efbd4dddc`, `0c227868f3f1b02fea3f195d1cc9f845d79c3822`.
* **Decisão de projeto:** Movi a regra de validação de horário da `Agenda` para a interface `RegraDisponibilidade` (Injeção de Dependência). Isso isola a responsabilidade de armazenamento e permite criar lógicas complexas de disponibilidade (como avaliar a duração dos serviços) sem alterar a `Agenda`.
* **Uso de IA:** Utilizei IA generativa atuando como assistente de engenharia de software para mapear potenciais violações SOLID no meu escopo (`Agenda` e `Agendamento`) e estruturar as abstrações de código e a redação formal da documentação. A decisão arquitetural, o código gerado e os testes foram avaliados por mim.

---

### Integrante: Jonathan do Nascimento Melo (`JonathanMelo0`)
**Agregado sob minha responsabilidade:** Barbeiro

---

#### Checkpoint 2 — Refatoração SOLID no Agregado Barbeiro

**Princípio aplicado:** SRP — Responsabilidade Única

**O que eu fiz:**

No Checkpoint 1, a classe `barbeiro` estava fazendo duas coisas ao mesmo tempo: guardar os dados do profissional (id, nome, agendamentos) e cuidar de toda a lógica de expediente — quais dias ele trabalha, horário de início e fim, se um determinado horário cabe dentro do turno. Qualquer ajuste numa regra de horário obrigava a abrir a entidade principal do agregado, e aí você corre o risco de introduzir um bug em código que nem tem relação com o que estava sendo mudado.

A solução foi criar o `JornadaTrabalho`, um Value Object imutável (`@dataclass(frozen=True)`), que concentra tudo que é regra de expediente num lugar só. A classe `barbeiro` passou a simplesmente delegar para esse objeto quando precisa saber se pode atender num horário ou não.

**Arquivos alterados:**

| Arquivo | O que mudou |
|---|---|
| `src/BarberTime/domain/model.py` | Criação do `JornadaTrabalho` com os métodos de expediente; `barbeiro` refatorado para delegar via propriedade sincronizada com o ORM. |
| `tests/unit/test_barbeiro.py` | 4 testes novos (testando o `JornadaTrabalho` isolado e integrado ao `barbeiro`) + 12 originais mantidos = 16 no total. |
| `docs/solid.md` | Minha seção com a análise da violação, hashes de antes e depois, testes e custo/benefício. |

**Hashes dos commits:**

| Marco | Hash |
|---|---|
| Último commit com a violação (antes) | `f30f823` |
| Refatoração SRP | `dd39e94` |
| Testes unitários do SRP | `adddd3e` |

**Por que ficou assim:** Mantive os atributos `horario_inicio`, `horario_fim` e `dias_trabalho` como colunas diretas no `barbeiro` para não quebrar o mapeamento do SQLAlchemy imperativo — o ORM não chama o `__init__` ao hidratar objetos do banco, então as colunas precisam existir como atributos diretos. A propriedade `jornada` constrói e mantém o `JornadaTrabalho` sincronizado a partir dessas colunas. Não precisei mexer no banco nem no mapeamento dos colegas.

**Uso de IA:** Usei o agente Antigravity para explorar o repositório, pensar no design do `JornadaTrabalho` e redigir a documentação. O código foi revisado por mim, os testes rodaram localmente (104 passando, CI verde) e os commits foram feitos por mim.

---

## Fase 2 — Checkpoint 3 (Padrões de Projeto GoF)

### Integrante: Jonathan do Nascimento Melo (`JonathanMelo0`)
**Agregado sob minha responsabilidade:** Barbeiro

---

#### Checkpoint 3 — Aplicação do Padrão GoF State no Agregado Barbeiro

**Padrão aplicado:** State (GoF Comportamental)

**O que eu fiz:**
Para este Checkpoint 3, modelei e implementei o padrão GoF State para tratar o ciclo de vida e o status de disponibilidade do barbeiro. No mundo real, um barbeiro não atende clientes apenas porque o relógio está dentro do expediente; ele transita por diferentes momentos operacionais: atendimento normal (`DISPONIVEL`), férias regulamentares (`EM_FERIAS`), pausas pontuais de almoço ou capacitação (`EM_PAUSA`), ou inativação do profissional (`INATIVO`).

Em vez de poluir a entidade `barbeiro` com diversas variáveis booleanas e condicionais (`if/elif/else`), criei a hierarquia abstrata `EstadoBarbeiro` e as classes concretas para cada estado. A entidade `barbeiro` passa a delegar as operações `pode_atender` e `validar_agendamento` para o seu estado atual. Quando o barbeiro entra em férias (`barbeiro.entrar_em_ferias()`), qualquer tentativa de agendamento é imediatamente recusada com mensagem clara, mesmo que o horário caia em um dia e hora de expediente habitual. Também expus a operação na camada de serviços com `alterar_status_barbeiro`.

**Arquivos alterados:**

| Arquivo | O que mudou |
|---|---|
| `src/BarberTime/domain/model.py` | Implementação da classe abstrata `EstadoBarbeiro`, das subclasses `EstadoDisponivel`, `EstadoEmFerias`, `EstadoEmPausa` e `EstadoInativo`, e refatoração da entidade `barbeiro` para delegar para o estado atual com métodos de transição. |
| `src/BarberTime/service_layer/services.py` | Implementação do caso de uso `alterar_status_barbeiro` e integração das mensagens de erro na validação de agendamento. |
| `tests/unit/test_barbeiro.py` | 7 novos testes unitários validando estado inicial, bloqueio por férias, retorno de férias, pausa com motivo, desativação/reativação, transições inválidas e injeção polimórfica de estado. |
| `tests/unit/test_services.py` | 3 novos testes validando alteração de status via serviço, bloqueio de horário quando o barbeiro está de férias e rejeição de ações inválidas. |
| `docs/gof.md` | Documentação completa do padrão State contendo contexto, problema real resolvido, justificativa e alternativas descartadas, mapeamento dos participantes, diagrama de classes em Mermaid, testes e trade-offs. |

**Hashes dos commits:**

| Marco | Hash | Data |
|---|---|---|
| Implementação do padrão State e testes no domínio | `c16b32f` | 08/11/2026 |
| Integração na camada de serviços e testes de serviço | `aacb622` | 10/11/2026 |
| Documentação em `docs/gof.md` e autorrelato no `DECISIONS.md` | `2e1ea83` | 10/11/2026 |

**Decisão técnica (uma frase de justificativa):**
Apliquei o padrão GoF State para encapsular o ciclo de vida e as regras de disponibilidade do barbeiro em classes dedicadas, garantindo que o bloqueio de agendamentos em férias ou pausas ocorra sem encher a entidade raiz de desvios condicionais procedurais (`if/else`) e protegendo as transições válidas entre estados.

**Declaração de Uso de IA:**
Utilizei o assistente de IA Antigravity como suporte para discutir a melhor modelagem GoF para o agregado Barbeiro (avaliando State vs Strategy), desenhar o diagrama de classes em Mermaid e redigir a documentação detalhada em `docs/gof.md`. A implementação, os testes e os commits foram executados e validados por mim, garantindo que a suíte completa com 114 testes passasse com 100% de sucesso e CI verde.

---

### Integrante: Ruan do Nascimento Silva (`ruanlov`)
**Agregado sob minha responsabilidade:** Comissão

---

#### Checkpoint 3 — Aplicação do Padrão GoF Decorator no Agregado Comissão

**Padrão aplicado:** Decorator (GoF Estrutural)

**O que eu fiz:**
Neste Checkpoint 3, identifiquei que o Strategy (aplicado no Checkpoint 2) trocava algoritmos completos de comissão, mas não resolvia a *combinação* de complementos transitórios — bônus de meta, descontos de insumos e promoções pontuais — sem gerar uma explosão de subclasses (o `ComissaoBarbeiroJunior` já escondia um desconto de insumos embutido). Implementei o padrão **Decorator** criando a hierarquia `DecoradorComissao` e os decoradores concretos `ComissaoComBonusFixo`, `ComissaoComDescontoFixo` e `ComissaoComBonusPercentual`, que envolvem qualquer `EstrategiaComissao` e podem ser empilhados em cadeia. Por implementarem o mesmo contrato, `Comissao` e `gerar_comissao` os consomem sem nenhuma alteração.

**Arquivos alterados:**

| Arquivo | O que mudou |
|---|---|
| `src/BarberTime/domain/model.py` | Adição de `DecoradorComissao` (ABC) e três decoradores concretos (`ComissaoComBonusFixo`, `ComissaoComDescontoFixo`, `ComissaoComBonusPercentual`). |
| `tests/unit/test_comissao.py` | 11 novos testes de domínio exercitando composição, transparência e validações. |
| `tests/unit/test_services_comissao.py` | 2 novos testes de serviço usando decoradores via `gerar_comissao`. |
| `docs/gof.md` | Documentação completa do padrão Decorator com os 7 itens do barema. |

**Hashes dos commits:**

| Marco | Hash |
|---|---|
| Implementação do Decorator no domínio (`model.py`) | `d1f1e47` |
| Testes unitários do Decorator (domínio + serviço) | `27992b5` |
| Documentação em `docs/gof.md` e autorrelato no `DECISIONS.md` | `7070602` |

**Decisão técnica (uma frase):**
Apliquei o padrão GoF Decorator para permitir compor bônus e taxas dinâmicos sobre a comissão base por delegação em cadeia, eliminando a explosão combinatória de subclasses que surgiria se cada combinação de repasse virasse uma nova `EstrategiaComissao`.

**Declaração de Uso de IA:**
Utilizei o auxílio de ferramentas de IA generativa durante o desenvolvimento. Todo o conteúdo gerado foi lido e aprovado por mim.

---

### Integrante: Marcello Bimbatti Mazzochi (`marcellomazzochi`)
**Agregado sob minha responsabilidade:** Agenda

#### Checkpoint 3 (GoF): Strategy

  * **O que foi feito:** Implementação do padrão GoF Strategy para regras de validação de disponibilidade no agregado Agenda/Agendamento (`src/BarberTime/domain/model.py`), testes automatizados (`tests/test_gof_agenda_strategy.py`) e documentação em `docs/gof.md`.
  * **Commits:** `6bd34bda0daf7128e1b662dc110daff6fbd51324` `6b019febd8faa71ba561fb4514273f77cdb1ec03` `d64694d3d0083f44f23e85505fb9f58e17a341f7` `3e0fa3deb5a10f32e294a3a4aab1459a040d2bee` `84babd7652d03112cf3e67b1267cd8ffa1e9c4d2`
  * **Decisão de projeto:** Isolar as regras de disponibilidade em objetos Strategy para permitir a troca entre validação simples por slot de horário e validação por intervalo temporal.
  * **Uso de IA generativa:** Utilizado IA generativa para atualizar o código com o padrão GOF, criar o diagrama Mermaid e gerar o suíte de testes unitários do pytest.

---

## Fase 2 — Entrega Final (Frameworks e Retrospectiva)

### Integrante: Jonathan do Nascimento Melo (`JonathanMelo0`)
**Agregado sob minha responsabilidade:** Barbeiro

---

#### Entrega Final — Análise de Frameworks, Retrospectiva e Reflexão Individual

**O que eu fiz:**
Para a entrega final da Fase 2, participei da elaboração dos dois documentos conclusivos do projeto:
1. Em `docs/frameworks.md`, conduzi a análise crítica dos três frameworks centrais adotados (Flask, SQLAlchemy e pytest). Detalhei o papel de cada um na solução, em qual camada atuam e por que o domínio permanece estritamente independente deles. Mapeei os pontos de Inversão de Controle (IoC no roteamento do Flask, no motor de fixtures do pytest e na hidratação de entidades no SQLAlchemy), apontei três padrões de projeto internos dos frameworks usados no nosso código (Data Mapper, Unit of Work e Decorator) e avaliei as consequências e trade-offs técnicos caso tivéssemos adotado um framework full-stack monolítico como o Django.
2. Em `docs/retrospectiva.md`, elaborei a retrospectiva arquitetural do projeto, revisitando as previsões do Checkpoint 1 (especialmente a alta velocidade dos testes em contraste com o overhead de camadas), reunindo as evidências reais da Fase 2 (refatoração SRP no Barbeiro, Strategy e Decorator na Comissão, e GoF State no ciclo de vida do Barbeiro) e defendendo a decisão final por uma arquitetura híbrida pragmática para a evolução futura da barbearia.

**Arquivos alterados:**

| Arquivo | O que mudou |
|---|---|
| `docs/frameworks.md` | Elaboração da análise completa de frameworks conforme a Seção 5.4 do edital. |
| `docs/retrospectiva.md` | Elaboração da retrospectiva arquitetural completa conforme a Seção 5.5 do edital. |
| `DECISIONS.md` | Registro do autorrelato da entrega final e do parágrafo de reflexão individual. |

**Hashes dos commits:**

| Marco | Hash | Data |
|---|---|---|
| Análise de Frameworks (`docs/frameworks.md`) | `7721312` | 15/11/2026 |
| Retrospectiva, reflexão individual e autorrelato (`docs/retrospectiva.md` e `DECISIONS.md`) | `c01f105` | 17/11/2026 |

**Decisão de projeto (uma frase de justificativa):**
Decidi defender uma arquitetura híbrida na retrospectiva, preservando a camada de serviços e o domínio puro para as regras complexas de negócio, mas simplificando o mapeamento de persistência para reduzir a fricção observada entre o ORM e os Value Objects durante a Fase 2.

**Declaração de Uso de IA:**
Utilizei o assistente de IA Antigravity para auxiliar na estruturação e revisão das seções conceituais de `docs/frameworks.md` e `docs/retrospectiva.md`, especialmente no levantamento dos pontos de inversão de controle e na formulação dos trade-offs comparativos com o Django. Todo o texto foi revisado, editado e alinhado com o código real do repositório por mim.

**Parágrafo de Reflexão Individual (Fase 2):**
A experiência na Fase 2 do projeto BarberTime foi transformadora para a minha maturidade como desenvolvedor e estudante de engenharia de software. Durante a Fase 1, a nossa principal preocupação era fazer as funcionalidades rodarem e passar nos primeiros testes, o que frequentemente resultava em misturar regras de calendário dentro da entidade e aceitar atalhos na persistência. Na Fase 2, ao sermos desafiados a olhar criticamente para o próprio código, percebi o abismo que existe entre um código que simplesmente funciona e uma arquitetura que acolhe mudanças sem quebrar. No meu agregado, o Barbeiro, refatorar a jornada de trabalho aplicando SRP e depois encapsular todo o ciclo de vida operacional com o padrão GoF State me mostrou na prática como o polimorfismo limpa o domínio e elimina cadeias confusas de condicionais. A maior dor foi sem dúvida o atrito com o mapeamento imperativo do SQLAlchemy, que nos obrigou a sincronizar atributos manuais para contornar a hidratação sem construtor. Se fosse começar o projeto hoje, eu teria optado pelo mapeamento declarativo moderno do SQLAlchemy 2.0 com dataclasses, simplificando as consultas de leitura e mantendo o foco total nas invariantes reais de negócio, sem carregar o peso de um framework monolítico como o Django.

---

### Integrante: Ruan do Nascimento Silva (`ruanlov`)
**Agregado sob minha responsabilidade:** Comissão

---

#### Entrega Final — Reflexão Individual e Autorrelato

**O que eu fiz:**
Para a entrega final da Fase 2, contribuí com a perspectiva do agregado Comissão na análise coletiva de frameworks e na retrospectiva arquitetural — em especial no mapeamento dos value objects `PercentualComissao` e `ServicoRealizado` via `composite` no SQLAlchemy e na evidência dos padrões Strategy e Decorator aplicados ao cálculo de comissão — e redigi meu parágrafo de reflexão individual na Parte 2 do `DECISIONS.md`.

**Arquivos alterados:**

| Arquivo | O que mudou |
|---|---|
| `DECISIONS.md` | Registro do autorrelato da entrega final e do parágrafo de reflexão individual do agregado Comissão. |

**Hashes dos commits:**

| Marco | Hash | Data |
|---|---|---|
| Reflexão individual e autorrelato final (`DECISIONS.md`) | `42fffec` | 17/11/2026 |

**Decisão de projeto (uma frase de justificativa):**
Decidi defender a manutenção da arquitetura em camadas para o agregado Comissão, porque foi ela que permitiu aplicar os padrões Strategy e Decorator sem alterar a entidade `Comissao` nem a função `gerar_comissao`, mesmo reconhecendo o custo de indireção do mapeamento imperativo.

**Declaração de Uso de IA:**
Utilizei ferramentas de IA generativa como apoio durante o desenvolvimento. A IA foi usada apenas como ferramenta auxiliar; todo o conteúdo foi lido, revisado e aprovado por mim.

**Parágrafo de Reflexão Individual (Fase 2):**
Na Fase 2, o agregado Comissão foi o meu laboratório para entender o custo e o valor de manter o domínio desacoplado. No Checkpoint 2, percebi que o cálculo de comissão violava o Princípio Aberto/Fechado: sem a hierarquia `EstrategiaComissao`, cada nova política de repasse (percentual fixo, sênior, júnior) exigiria abrir a entidade `Comissao`. No Checkpoint 3, o Decorator mostrou que a composição por delegação é mais poderosa do que uma família de estratégias fechadas, pois me deixou combinar bônus e descontos sem criar uma subclasse para cada combinação. O que mais me marcou foi descobrir que a arquitetura em camadas tornou essas mudanças quase gratuitas: apliquei dois padrões sem tocar na entidade `Comissao` nem na função `gerar_comissao`, e os `FakeRepositories` validaram tudo em memória. Paguei o preço na persistência: mapear os value objects `PercentualComissao` e `ServicoRealizado` com `composite` e lidar com o percentual nulo na serialização. Se recomeçasse, eu modelaria a senioridade do barbeiro no domínio desde o início, para que a política de comissão fosse decidida pela entidade, e não por estratégias injetadas manualmente a cada chamada.


### Integrante: Johnny de Godoy (`johnn2c`)
**Agregado sob minha responsabilidade:** Fidelidade

#### Entrega Final — Reflexão Individual e Autorrelato

**O que eu fiz:**

Para a entrega final do projeto BarberTime, contribuí com a evolução e documentação do agregado Fidelidade, além da análise arquitetural realizada durante a Fase 2.

No desenvolvimento do agregado Fidelidade, trabalhei na implementação das regras de negócio responsáveis por controlar a quantidade de cortes realizados pelo cliente e verificar as condições necessárias para a concessão de benefícios. Também participei da criação dos testes unitários, dos repositórios para persistência dos dados, da integração com a camada de serviços e da disponibilização das funcionalidades por meio das rotas da aplicação.

Na Fase 2, contribuí com a análise comparativa entre a arquitetura adotada pelo projeto, baseada em Ports & Adapters, Repository e Service Layer, e a alternativa Active Record + Transaction Script. Essa análise considerou aspectos como manutenibilidade, testabilidade e desempenho, resultando na recomendação de manter a arquitetura atual. Também participei da documentação da decisão relacionada ao isolamento dos testes unitários por meio de um ADR.

**Arquivos relacionados:**

| Arquivo | O que foi desenvolvido |
|---|---|
| `src/BarberTime/domain/model.py` | Implementação do agregado Fidelidade e suas regras de negócio. |
| `src/BarberTime/adapters/repository.py` | Estrutura dos repositórios relacionados à fidelidade. |
| `src/BarberTime/service_layer/services.py` | Implementação das operações e regras de serviço relacionadas à fidelidade. |
| `src/BarberTime/entrypoints/` | Integração das funcionalidades de fidelidade com as rotas da aplicação. |
| `tests/` | Criação de testes unitários e de integração para validar o funcionamento do agregado. |
| `docs/arquitetura.md` | Análise comparativa entre a arquitetura atual e a alternativa Active Record + Transaction Script. |
| `docs/adr/` | Documentação da decisão relacionada ao isolamento dos testes unitários. |

**Decisão de projeto (uma frase de justificativa):**

Decidi manter as regras de negócio da Fidelidade concentradas no domínio, separando a persistência, a execução dos casos de uso e a comunicação com a aplicação, pois essa organização facilita os testes, reduz o acoplamento e torna futuras alterações mais seguras.

**Declaração de Uso de IA:**

Utilizei ferramentas de inteligência artificial generativa como apoio durante o desenvolvimento e a documentação do projeto, principalmente para esclarecer conceitos de arquitetura, auxiliar na organização das justificativas técnicas e revisar os textos produzidos. As sugestões foram utilizadas como suporte ao trabalho, sendo necessário compreender e avaliar sua aplicação de acordo com a estrutura e os requisitos do projeto.

**Parágrafo de Reflexão Individual (Fase 2):**

Durante o desenvolvimento do BarberTime, pude perceber na prática que implementar uma funcionalidade vai muito além de fazer com que ela funcione. No início, meu foco estava principalmente em desenvolver as regras da Fidelidade e garantir que elas fossem executadas corretamente. Ao longo do projeto, entretanto, compreendi a importância de organizar essas regras dentro de uma arquitetura que permita testar, manter e evoluir o sistema sem comprometer outras partes da aplicação. Trabalhar com o agregado Fidelidade me ajudou a entender melhor a separação entre domínio, persistência e serviços, além de mostrar como os testes unitários e de integração contribuem para identificar problemas e aumentar a segurança das alterações. Outro aprendizado importante aconteceu durante a análise arquitetural da Fase 2, quando precisei comparar diferentes abordagens e avaliar seus impactos na manutenção e na testabilidade do software. Essa atividade me fez perceber que nem sempre a solução mais simples de implementar é a melhor para manter no longo prazo. Se fosse iniciar o projeto novamente, daria  mais atenção à definição das responsabilidades de cada camada desde o começo, buscando evitar acoplamentos desnecessários e facilitando a evolução das funcionalidades. Considero que o projeto foi importante para transformar conhecimentos teóricos de engenharia de software em experiências práticas, principalmente em relação à organização do código.