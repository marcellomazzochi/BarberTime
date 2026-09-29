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

#### Declaração de Uso de IA e Simplificações
- **Uso de IA:** Conforme as regras da Seção 2.5, usei assistente de IA para tirar dúvidas pontuais de sintaxe do SQLAlchemy 2.0 no mapeamento de objetos de valor com `composite` e para revisar a estrutura dos arquivos `test_*`. As regras de negócio do agregado Comissão (status do atendimento, cálculo do percentual, pertencimento ao barbeiro), o modelo e todos os testes foram pensados e escritos para o nosso domínio. Também usei a IA para conferir se o estilo seguia o que os colegas já tinham implementado.
- **Simplificações conscientes:** Nesta Fase 1 guardo o status do atendimento como um enum em coluna única e o serviço realizado como snapshot em três colunas (`servico_nome`, `servico_duracao`, `servico_preco`) na própria tabela `atendimentos`. Isso evita criar uma tabela associativa de serviços e uma junção a mais, mantendo a comissão desacoplada do cadastro de serviços. O percentual padrão da comissão ficou como 10%, podendo ser sobrescrito por atendimento; a comissão não tem estorno/cancelamento nesta fase.
