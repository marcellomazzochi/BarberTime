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

## Fase 1 — Proposta inicial

**Data registrada:** 27/09/2026  
**Período estimado de elaboração:** semana de 21 a 27/09/2026.

**Atividade:** elaboração e atualização da proposta inicial do projeto BarberTime.

**Arquivo principal:**
- `PROPOSTA.md`

**Commit:**
- `e7d3178` — Update PROPOSTA.md

**Descrição:** participei da elaboração da proposta inicial do BarberTime, contribuindo para a documentação que orienta o desenvolvimento do sistema.


**checkpoint 2**

-**Período estimado de desenvolvimento:** 21 a 22/10/2026.

**Responsabilidade:** implementação do agregado `Fidelidade`, incluindo regras de domínio, testes, persistência, repositórios, serviços e rotas.

### Atividades realizadas

- Criei e ajustei o agregado `Fidelidade`, estruturando as regras de negócio relacionadas à fidelidade dos clientes.
- Desenvolvi testes unitários para verificar o comportamento do agregado e suas regras.
- Refatorei os casos de teste para melhorar a organização e a validação do comportamento esperado.
- Implementei a tabela de fidelidade e os repositórios necessários para a persistência dos dados.
- Desenvolvi funções na camada de serviços para executar os casos de uso relacionados à fidelidade.
- Implementei o registro de `no_show` na classe `Fidelidade`.
- Desenvolvi um teste de integração para verificar o funcionamento conjunto dos componentes.
- Adicionei as rotas de fidelidade para disponibilizar as funcionalidades por meio da aplicação.
- Realizei ajustes para compatibilizar a implementação com os testes do projeto.

### Commits relacionados

- `a3a3e42` — adicionado agregado de fidelidade
- `154a7a5` — feat: criados testes unitários de fidelidade
- `f8e6176` — adicionado agregado de fidelidade
- `5a0074a` — adicionado atendimento aos testes de fidelidade
- `cb59b47` — adiciona tabela de fidelidade
- `197742` — adicionados repositórios de fidelidade
- `fe6fca` — adicionado teste de integração de fidelidade
- `448f543` — adicionado registrar_no_show na classe fidelidade
- `4d13e7f` — adicionadas funções de fidelidade
- `63f4de8` — adicionadas rotas de fidelidade

### Decisão técnica

A implementação da fidelidade foi organizada em componentes de domínio, persistência, serviços e rotas, mantendo as responsabilidades separadas. Os testes unitários foram utilizados para validar as regras do agregado, enquanto o teste de integração foi adicionado para verificar a interação entre componentes.


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
## Integrante Johnny de Godoy (`johnn2c`)

### Fase 2 — Documentação e análise arquitetural


**Data dos commits:** 22/10/2026  
**Período estimado:** 22/10/2026.

### Atividades realizadas

- Atualizei `docs/arquitetura.md` para registrar a análise arquitetural.
- Adicionei a Seção 5, comparando a arquitetura adotada com a alternativa Active Record + Transaction Script.
- Comparei as abordagens pelos atributos de manutenibilidade, testabilidade e desempenho.
- Registrei a conclusão de manter a arquitetura atual, considerando os padrões exigidos no projeto.
- Documentei a decisão relacionada ao isolamento dos testes unitários por meio de um ADR.
- Ajustei o identificador do ADR para manter a documentação consistente.

### Arquivos relacionados

- `docs/arquitetura.md`
- `docs/adr/` — ADR de isolamento dos testes unitários e arquivo com identificador atualizado.

### Commits relacionados

- `f6cfde` — Adicionada seção 5
- `64ca6bb` — atualização arquitetura
- `54b2ac6` — adicionado ADR de isolamento dos testes unitários
- `7c30b43` — alterado identificador do ADR

### Decisão técnica

A análise comparativa considera a arquitetura atual baseada em Ports & Adapters, Repository e Service Layer e a alternativa Active Record + Transaction Script. A recomendação é manter os padrões atuais, considerando a separação das responsabilidades e a testabilidade. A alternativa foi analisada documentalmente, não implementada como substituição da arquitetura do projeto.

### Uso de IA generativa

Utilizei o ChatGPT como ferramenta de apoio para compreender os requisitos da atividade,  revisar a documentação e organizar as justificativas técnicas. As sugestões foram usadas apenas como apoio.

### Observação sobre o histórico

As datas foram organizadas a partir do histórico de commits disponível. Os períodos identificados como estimados representam aproximações do período de trabalho, e não necessariamente o horário ou o dia em que cada atividade foi iniciada.


