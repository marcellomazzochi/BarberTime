# Padrões de Projeto GoF — BarberTime

Este documento registra a aplicação dos padrões de projeto GoF (*Gang of Four*) no sistema **BarberTime**, conforme os requisitos da **Fase 2 — Checkpoint 3**.

Cada integrante é responsável por implementar e documentar um padrão GoF distinto em seu respectivo módulo/agregado, resolvendo um problema real do domínio da barbearia.

---

## Seção: Jonathan do Nascimento Melo — Agregado Barbeiro

### 1. Nome e Categoria do Padrão

* **Nome do Padrão:** State
* **Categoria:** Comportamental (*Behavioral Pattern*)
* **Definição clássica (GoF):** *"Permite que um objeto altere o seu comportamento quando o seu estado interno muda. O objeto parecerá ter mudado de classe."*

---

### 2. Contexto no Sistema e Problema que ele Resolve

#### 2.1 Contexto do Agregado Barbeiro
No sistema BarberTime, o agregado **Barbeiro** tem como invariante fundamental:
> *"Impedir agendamentos fora do horário de trabalho."*

No Checkpoint 2, extraí a validação de expediente para o Value Object imutável `JornadaTrabalho`. Isso garantiu que horários antes do início, após o término e dias de folga semanal fossem validados de forma isolada e coesa.

#### 2.2 O Problema do Mundo Real
No entanto, no dia a dia operacional de uma barbearia real, a disponibilidade de um profissional não depende apenas de um relógio ou de uma folha de calendário semanal fixa. Barbeiros passam por diferentes **momentos e transições de ciclo de vida funcional**:

1. **Disponível (`DISPONIVEL`):** O barbeiro está em atividade regular e apto a receber agendamentos dentro da sua jornada de trabalho habitual.
2. **Em Férias (`EM_FERIAS`):** O profissional está em gozo de férias regulamentares. Durante esse período, **qualquer agendamento deve ser expressamente bloqueado**, independentemente do horário solicitado coincidir com o expediente padrão. O sistema deve emitir um retorno imediato e explicativo ao cliente ou atendente, sem nem precisar processar horários de início e fim.
3. **Em Pausa / Licença Temporária (`EM_PAUSA`):** O barbeiro precisa se ausentar pontualmente durante o expediente (ex: intervalo prolongado de almoço, treinamento em nova técnica de degradê/barba, consulta médica emergencial). Agendamentos são temporariamente bloqueados com o registro do motivo correspondente.
4. **Inativo (`INATIVO`):** O profissional foi desligado ou desativado temporariamente do sistema. Nenhuma operação de atendimento pode ser realizada e operações normais de ciclo de vida (como solicitar férias) são impedidas até que haja uma reativação expressa.

#### 2.3 Por que o design anterior não atendia
Se tentássemos acomodar esse ciclo de vida com flags booleanas (`em_ferias: bool`, `ativo: bool`, `em_pausa: bool`) na própria classe `barbeiro`, teríamos:
- Proliferação de condicionais encadeadas (`if self.em_ferias: ... elif not self.ativo: ... elif self.em_pausa: ...`) espalhadas por múltiplos métodos (`pode_atender`, `validar_agendamento`, `adicionar_agendamento`, etc.).
- Alto risco de inconsistências de estado: o que acontece se alguém marcar `em_ferias = True` e `ativo = False` ao mesmo tempo?
- Violação do Princípio Aberto/Fechado (OCP): a adição de um novo estado funcional (ex.: licença maternidade/paternidade) obrigaria a reabrir e modificar todos os métodos da entidade de domínio principal.

O padrão **State** resolve esse problema ao encapsular o comportamento e as restrições de cada fase do ciclo de vida em classes dedicadas, permitindo que a entidade `barbeiro` altere seu comportamento de agendamento em tempo de execução através da troca do objeto de estado.

---

### 3. Por que esse Padrão e Alternativas Consideradas

#### 3.1 Alternativa 1 Considerada: Flags Booleanas e Condicionais Procedurais
* **Abordagem:** Incluir campos como `self.em_ferias = False` e `self.ativo = True` na classe `barbeiro`, checando essas variáveis antes de cada validação.
* **Por que foi descartada:** Gera código engessado e difícil de manter. Cada novo status operacional exigiria modificar `barbeiro.py` em diversos pontos, violando o SRP e o OCP. Além disso, as transições válidas de estado (quem pode transitar para onde) ficariam sem proteção, facilitando combinações de dados inválidas.

#### 3.2 Alternativa 2 Considerada: Padrão Strategy
* **Abordagem:** Criar uma interface de estratégia intercambiável para checar a disponibilidade do profissional.
* **Por que foi descartada:** Embora estruturalmente parecidos (ambos usam composição e delegação polimórfica), o propósito semântico do Strategy é isolar uma família de algoritmos intercambiáveis de cálculo pontual sem estado interno duradouro (como o Ruan implementou com perfeição no cálculo de comissão sênior vs júnior no Checkpoint 2). Já o **State** modela uma **máquina de estados finita**, na qual o objeto transita ao longo do tempo por diferentes fases do seu ciclo de vida (`Disponivel` $\rightarrow$ `EmFerias` $\rightarrow$ `Disponivel` $\rightarrow$ `Inativo`), e cada estado conhece as regras permitidas de transição para os demais estados. Para o ciclo de vida do barbeiro, o State é o padrão conceitualmente exato segundo o GoF.

---

### 4. Participantes do Padrão Mapeados no Código Real

| Participante GoF | Classe / Elemento Real no Projeto | Localização | Papel no Sistema |
|---|---|---|---|
| **Context** | `barbeiro` (ou `Barbeiro`) | `src/BarberTime/domain/model.py` | Entidade raiz do agregado. Mantém a referência para o estado atual (`_estado`), delega a validação de disponibilidade e expõe métodos de transição (`entrar_em_ferias`, `retornar_ao_trabalho`, `pausar`, `desativar`, `reativar`). |
| **State (Interface Abstrata)** | `EstadoBarbeiro` | `src/BarberTime/domain/model.py` | Classe base abstrata (`abc.ABC`). Declara os métodos de comportamento (`pode_atender`, `validar_agendamento`) e transição com tratamento padrão defensivo contra transições ilegais. |
| **ConcreteState** | `EstadoDisponivel` | `src/BarberTime/domain/model.py` | Estado padrão ativo. Valida se a data/hora solicitada coincide com o expediente da `JornadaTrabalho`. Permite transição para férias, pausa ou inativo. |
| **ConcreteState** | `EstadoEmFerias` | `src/BarberTime/domain/model.py` | Bloqueia qualquer agendamento informando que o barbeiro está de férias. Permite transição para retorno ao trabalho ou desativação. |
| **ConcreteState** | `EstadoEmPausa` | `src/BarberTime/domain/model.py` | Bloqueia agendamentos temporariamente por motivo pontual (almoço, treinamento). Permite retorno ao trabalho ou desativação. |
| **ConcreteState** | `EstadoInativo` | `src/BarberTime/domain/model.py` | Bloqueia agendamentos e transições operacionais até que o barbeiro seja formalmente reativado. |

---

### 5. Diagrama de Classes (Mermaid)

```mermaid
classDiagram
    class barbeiro {
        +int id
        +str nome
        -EstadoBarbeiro _estado
        +JornadaTrabalho jornada
        +EstadoBarbeiro estado
        +str status
        +pode_atender(data_hora, duracao_minutos) bool
        +validar_agendamento(data_hora, duracao_minutos) void
        +adicionar_agendamento(agendamento) void
        +entrar_em_ferias() void
        +retornar_ao_trabalho() void
        +pausar(motivo) void
        +desativar() void
        +reativar() void
        +definir_estado(novo_estado) void
    }

    class EstadoBarbeiro {
        <<abstract>>
        +str nome*
        +pode_atender(barbeiro, data_hora, duracao_minutos)* bool
        +validar_agendamento(barbeiro, data_hora, duracao_minutos)* void
        +entrar_em_ferias(barbeiro) void
        +retornar_ao_trabalho(barbeiro) void
        +pausar(barbeiro, motivo) void
        +desativar(barbeiro) void
        +reativar(barbeiro) void
    }

    class EstadoDisponivel {
        +str nome = "DISPONIVEL"
        +pode_atender(barbeiro, data_hora, duracao_minutos) bool
        +validar_agendamento(barbeiro, data_hora, duracao_minutos) void
        +entrar_em_ferias(barbeiro) void
        +pausar(barbeiro, motivo) void
        +desativar(barbeiro) void
        +retornar_ao_trabalho(barbeiro) void
    }

    class EstadoEmFerias {
        +str nome = "EM_FERIAS"
        +pode_atender(barbeiro, data_hora, duracao_minutos) bool
        +validar_agendamento(barbeiro, data_hora, duracao_minutos) void
        +retornar_ao_trabalho(barbeiro) void
        +entrar_em_ferias(barbeiro) void
        +pausar(barbeiro, motivo) void
    }

    class EstadoEmPausa {
        +str motivo
        +str nome = "EM_PAUSA"
        +pode_atender(barbeiro, data_hora, duracao_minutos) bool
        +validar_agendamento(barbeiro, data_hora, duracao_minutos) void
        +retornar_ao_trabalho(barbeiro) void
        +pausar(barbeiro, motivo) void
        +entrar_em_ferias(barbeiro) void
    }

    class EstadoInativo {
        +str nome = "INATIVO"
        +pode_atender(barbeiro, data_hora, duracao_minutos) bool
        +validar_agendamento(barbeiro, data_hora, duracao_minutos) void
        +reativar(barbeiro) void
        +desativar(barbeiro) void
    }

    barbeiro o-- EstadoBarbeiro : delega para estado atual
    EstadoBarbeiro <|-- EstadoDisponivel : herda e implementa
    EstadoBarbeiro <|-- EstadoEmFerias : herda e implementa
    EstadoBarbeiro <|-- EstadoEmPausa : herda e implementa
    EstadoBarbeiro <|-- EstadoInativo : herda e implementa
```

---

### 6. Testes Automatizados que Exercitam o Padrão

Foram implementados testes unitários tanto na camada de domínio quanto na camada de serviços para validar exaustivamente as invariantes do padrão:

#### 6.1 Testes Unitários de Domínio (`tests/unit/test_barbeiro.py`)
1. **`test_estado_inicial_do_barbeiro_e_disponivel`:** Garante que toda nova instância nasce no `EstadoDisponivel`, mantendo integridade com instâncias já existentes e preservando retrocompatibilidade com o banco de dados.
2. **`test_transicao_para_estado_em_ferias_bloqueia_agendamentos`:** Exercita a chamada `b.entrar_em_ferias()`. Comprova que `b.pode_atender(...)` retorna `False` e `b.validar_agendamento(...)` levanta `ValueError` contendo `"periodo de ferias"`, mesmo quando a requisição é feita para um dia e horário perfeitamente válidos no expediente habitual.
3. **`test_retorno_ao_trabalho_apos_ferias_restaura_disponibilidade`:** Valida o retorno funcional chamando `b.retornar_ao_trabalho()`, confirmando que o barbeiro volta ao estado `DISPONIVEL` e aceita agendamentos normalmente.
4. **`test_estado_em_pausa_bloqueia_atendimento_com_motivo`:** Testa a transição para `EstadoEmPausa(motivo="Horario de almoco")` e assegura que a mensagem de erro detalha a causa da indisponibilidade.
5. **`test_desativacao_e_reativacao_do_barbeiro`:** Valida o ciclo completo de desativação (`INATIVO`) e reativação (`DISPONIVEL`), comprovando que um barbeiro inativo não pode transitar para férias sem ser previamente reativado.
6. **`test_transicoes_invalidas_entre_estados`:** Garante a proteção da máquina de estados, rejeitando ações inconsistentes (ex: tentar colocar em férias um barbeiro que já está de férias).
7. **`test_injecao_polimorfica_de_estado_no_construtor`:** Prova que o construtor do `barbeiro` aceita injeção direta de qualquer subclasse de `EstadoBarbeiro`, atestando o baixo acoplamento.

#### 6.2 Testes de Serviço (`tests/unit/test_services.py`)
* **`test_service_alterar_status_barbeiro_ferias_e_retorno`:** Comprova a orquestração do caso de uso de alteração de status através de `services.alterar_status_barbeiro`.
* **`test_service_validar_horario_bloqueado_quando_barbeiro_em_ferias`:** Valida que o caso de uso `services.validar_horario_atendimento` respeita a máquina de estados do domínio e rejeita agendamentos de profissionais de férias.

---

### 7. Análise de Custo e Benefício da Aplicação do Padrão

#### 7.1 Benefícios Concretos
- **Eliminação de condicionais complexas:** Removeu-se completamente a necessidade de blocos `if/elif/else` aninhados dentro da raiz do agregado.
- **Transições de ciclo de vida seguras:** A própria hierarquia de estados valida se a transição solicitada é legal, impedindo inconsistências de domínio.
- **Extensibilidade e OCP:** Se a barbearia quiser incluir um novo estado (por exemplo, `EstadoAfastamentoMedico` ou `EstadoAtendimentoExterno`), basta criar uma nova subclasse de `EstadoBarbeiro` sem alterar uma única linha dos estados estáveis existentes.
- **Retrocompatibilidade transparente:** Na ausência de estado explícito (inclusive na hidratação imperativa de objetos via SQLAlchemy), o barbeiro assume automaticamente o `EstadoDisponivel`, garantindo que toda a suíte pré-existente continue verde sem necessidade de refazer o esquema do banco.

#### 7.2 Custos e Trade-offs
- **Proliferação de classes no módulo:** Adicionaram-se cinco novas classes (`EstadoBarbeiro`, `EstadoDisponivel`, `EstadoEmFerias`, `EstadoEmPausa`, `EstadoInativo`). Para um sistema excessivamente simples onde barbeiros nunca se ausentam, isso representaria uma sobrecarga estrutural. Porém, para uma barbearia com operação real, essa divisão reflete o domínio com fidelidade.
- **Camada adicional de indireção:** O método `barbeiro.validar_agendamento` delega para `self.estado.validar_agendamento`, que por sua vez consulta a `jornada` do barbeiro quando disponível. Essa navegação de chamada é um custo consciente em troca de clareza e separação de responsabilidades.
