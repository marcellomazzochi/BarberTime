# Análise SOLID — BarberTime

## Seção: Ruan do Nascimento Silva — Agregado Comissão

---

### 1. Princípio Escolhido

**OCP — Princípio Aberto/Fechado** (*Open/Closed Principle*)

> "Entidades de software (classes, módulos, funções) devem ser abertas para extensão, mas fechadas para modificação."  
> — Bertrand Meyer (1988), consolidado por Robert C. Martin (Clean Architecture)

---

### 2. Identificação da Violação (código anterior a 06/10)

#### 2.1 O Código Original

No código entregue no **Checkpoint 1** (commit `7a93494`), o construtor da classe `Comissao` em `src/BarberTime/domain/model.py` assumia diretamente a responsabilidade pela definição algorítmica do valor a ser pago, empregando inclusive um percentual-padrão fixo de 10% codificado de forma rígida (*hardcoded*):

```python
# model.py — ANTES da refatoração (commit 7a93494)
class Comissao:
    def __init__(self, id, atendimento, percentual=None, barbeiro=None):
        ...
        if percentual is None:
            percentual = PercentualComissao(10.0)   # 10% hardcoded
        elif not isinstance(percentual, PercentualComissao):
            percentual = PercentualComissao(percentual)

        self.percentual = percentual
        self.valor = percentual.aplicar(atendimento.servico.preco)
```

E na camada de serviço (`services.py`), a função `gerar_comissao` limitava-se a repassar um valor escalar de `percentual`:

```python
# services.py — ANTES da refatoração
comissao = Comissao(id=comissao_id, atendimento=atendimento, percentual=percentual)
```

#### 2.2 Mudança de Requisito que Expõe a Violação do OCP

Considere uma evolução comum nas regras de remuneração de uma barbearia:

> **"A partir de novembro, barbeiros classificados como *sênior* recebem 15% de comissão sobre o serviço. Barbeiros *júnior* recebem 10%, porém com uma dedução de R$ 5,00 correspondente ao rateio de custos de insumos (produtos utilizados no corte)."**

Diante dessa nova necessidade de negócio, o design original colapsa frente ao **Princípio Aberto/Fechado**. A única forma de acomodar a diferenciação de perfis e a dedução de insumos seria **reabrir a classe `Comissao` e modificar o seu construtor** com desvios condicionais:

```python
# VIOLAÇÃO DO OCP — modificação direta de código existente e estável
class Comissao:
    def __init__(self, id, atendimento, percentual=None, nivel_barbeiro=None, ...):
        ...
        # A classe de domínio é forçada a conhecer particularidades de cada perfil
        if nivel_barbeiro == "senior":
            percentual = PercentualComissao(15.0)
        elif nivel_barbeiro == "junior":
            bruto = PercentualComissao(10.0).aplicar(atendimento.servico.preco)
            self.valor = max(0.0, bruto - 5.0)
            return
        else:
            percentual = percentual or PercentualComissao(10.0)
        ...
```

A cada nova regra de comissionamento (ex.: comissão progressiva por metas, bonificações em feriados ou taxas diferenciadas por tipo de procedimento), a classe `Comissao` teria que sofrer novas edições cirúrgicas, violando frontalmente a estabilidade do agregado.

#### 2.3 O Problema Concreto de Acoplamento

A dependência direta entre a entidade `Comissao` e a fórmula matemática de cálculo gerava os seguintes problemas arquiteturais:

| Sintoma de Acoplamento | Consequência Prática |
|---|---|
| **Acoplamento forte à lógica de cálculo** | A entidade central do agregado conhecia os detalhes de como apurar o valor. Mudar uma taxa ou dedução exigia alterar a própria entidade de domínio. |
| **Rigidez contra novas políticas (Violação do OCP)** | O código era *fechado para extensão*: não havia mecanismo polimórfico para plugar uma nova regra sem adulterar o código-fonte existente. |
| **Fragilidade e risco de regressão** | Modificar `Comissao.__init__` para atender barbeiros juniores colocava em risco o fluxo estável de barbeiros padrão já em produção. |
| **Violação secundária do SRP** | A classe acumulava duas razões para mudar: alteração nas invariantes de existência da comissão (ex.: exigir atendimento concluído) e alteração na fórmula financeira de remuneração. |
| **Dificuldade de teste unitário isolado** | Não era possível validar regras de desconto ou taxas complexas sem instanciar toda a estrutura de `Atendimento`, `barbeiro` e `servico`. |

---

### 3. A Refatoração — Princípio Aberto/Fechado (OCP)

#### 3.1 Hashes Git

| Marco | Hash |
|---|---|
| Último commit antes da refatoração | `350a58b` |
| Commit que introduz a refatoração (OCP) | `84dd28c` |

#### 3.2 Solução Arquitetural: Isolamento de Volatilidade via Abstração

Para restabelecer a conformidade com o **OCP**, a lógica volátil de cálculo de remuneração foi completamente desacoplada do ciclo de vida da entidade `Comissao`. 

A tática de design adotada foi a aplicação do **Padrão Strategy**: define-se um contrato abstrato comum para o cálculo e injetam-se implementações polimórficas intercambiáveis. Com isso:
- A classe `Comissao` torna-se **fechada para modificação**: o seu código permanece imutável perante novas políticas de repasse.
- O sistema torna-se **aberto para extensão**: qualquer nova regra passa a ser introduzida como uma nova classe que implementa o contrato abstrato, sem tocar em nenhuma linha do domínio preexistente.

```python
# domain/model.py — Contrato abstrato e extensões polimórficas
class EstrategiaComissao(abc.ABC):
    """Contrato abstrato que isola a regra de cálculo de comissão."""
    @abc.abstractmethod
    def calcular(self, preco_servico: float) -> float:
        """Calcula e retorna o valor líquido da comissão devida."""
        raise NotImplementedError


class ComissaoPercentualFixo(EstrategiaComissao):
    """Estratégia padrão: preserva o comportamento legado de taxa percentual."""
    def __init__(self, percentual: float | PercentualComissao = 10.0):
        if isinstance(percentual, PercentualComissao):
            self._percentual = percentual
        else:
            self._percentual = PercentualComissao(percentual)

    @property
    def percentual(self) -> PercentualComissao:
        return self._percentual

    def calcular(self, preco_servico: float) -> float:
        return self._percentual.aplicar(preco_servico)


class ComissaoBarbeiroSenior(EstrategiaComissao):
    """Nova regra estendida: remuneração fixa de 15% para profissionais seniores."""
    _PERCENTUAL = PercentualComissao(15.0)

    def calcular(self, preco_servico: float) -> float:
        return self._PERCENTUAL.aplicar(preco_servico)


class ComissaoBarbeiroJunior(EstrategiaComissao):
    """Nova regra estendida: taxa de 10% com dedução de insumos de R$ 5,00."""
    _PERCENTUAL = PercentualComissao(10.0)
    DESCONTO_INSUMOS: float = 5.0

    def calcular(self, preco_servico: float) -> float:
        bruto = self._PERCENTUAL.aplicar(preco_servico)
        return round(max(0.0, bruto - self.DESCONTO_INSUMOS), 2)
```

#### 3.3 A Inversão no Agregado `Comissao`

A classe `Comissao` agora delega a computação à abstração injetada, atingindo a separação limpa de responsabilidades e eliminando acoplamentos rígidos:

```python
class Comissao:
    def __init__(
        self,
        id,
        atendimento,
        percentual=None,
        barbeiro=None,
        estrategia: EstrategiaComissao | None = None,
    ):
        ...
        # Injeção da estratégia com fallback retrocompatível
        if estrategia is not None:
            self._estrategia = estrategia
            self.percentual = (
                estrategia.percentual if isinstance(estrategia, ComissaoPercentualFixo) else None
            )
        else:
            # Mantém compatibilidade com chamadas legadas escalares
            percentual_vo = (
                PercentualComissao(10.0) if percentual is None
                else (percentual if isinstance(percentual, PercentualComissao) else PercentualComissao(percentual))
            )
            self._estrategia = ComissaoPercentualFixo(percentual_vo)
            self.percentual = percentual_vo

        self.id = id
        self.atendimento = atendimento
        self.barbeiro = barbeiro
        # Delegação estrita à abstração (OCP cumprido)
        self.valor = self._estrategia.calcular(atendimento.servico.preco)
```

Representação estrutural da desacoplagem:

```
                  ┌──────────────────────┐
                  │       Comissao       │
                  │ (Fechada p/ mudança) │
                  └──────────┬───────────┘
                             │ delega cálculo
                             ▼
                  ┌──────────────────────┐
                  │  EstrategiaComissao  │ ◀─── [Contrato / Abstração]
                  │       (ABC)          │
                  └──────────▲───────────┘
                             │
     ┌───────────────────────┼───────────────────────┐
     │                       │                       │
┌────┴─────────────────┐ ┌───┴──────────────────┐ ┌──┴──────────────────┐
│ComissaoPercentualFixo│ │ComissaoBarbeiroSenior│ │ComissaoBarbeiroJunior│
│  (Legado: 10% base)  │ │ (Extensão: 15% fixo) │ │ (Extensão: 10% - R$5)│
└──────────────────────┘ └──────────────────────┘ └──────────────────────┘
                   ▲
                   │ [Aberto para novas extensões sem alterar Comissao]
```

#### 3.4 Retrocompatibilidade Garantida

A função `gerar_comissao` em `src/BarberTime/service_layer/services.py` foi atualizada para receber opcionalmente `estrategia: EstrategiaComissao | None = None`. Caso nenhum parâmetro polimórfico seja fornecido, o comportamento preexistente de percentual fixo é integralmente preservado, sem quebrar APIs ou clientes existentes.

---

### 4. Garantia dos Testes

A integridade do comportamento anterior e a validação do desacoplamento foram atestadas por meio de testes automatizados:

| Arquivo de Teste | Quantidade Anterior | Quantidade Atual | Escopo Coberto |
|---|---|---|---|
| `tests/unit/test_comissao.py` | 16 testes | **27 testes** | Invariantes de conclusão, validação de limites e testes das novas estratégias polimórficas |
| `tests/unit/test_services_comissao.py` | 12 testes | **16 testes** | Orquestração da camada de serviços com e sem injeção de estratégias |
| **Total do Agregado** | **28 testes** | **43 testes** | **100% de aprovação (0 regressões)** |

Casos de teste representativos da correção do OCP:
- `test_estrategia_e_abc_nao_pode_ser_instanciada_diretamente`: assegura a invariante da interface abstrata.
- `test_estrategia_senior_calcula_15_porcento`: valida a regra do barbeiro sênior de forma estritamente isolada do banco e de atendimentos.
- `test_estrategia_junior_nao_retorna_valor_negativo`: testa o piso financeiro na dedução de insumos.
- `test_nova_estrategia_sem_modificar_comissao`: cria uma estratégia inédita em tempo de execução e a injeta em `Comissao`, comprovando experimentalmente que a classe está aberta a extensão sem necessidade de modificação.
- `test_comissao_estrategia_e_legado_percentual_sao_equivalentes_para_padrao`: garante regressão zero contra chamadas legadas.

---

### 5. Análise Crítica — Trade-offs da Refatoração

A decisão de refatorar para cumprir o Princípio Aberto/Fechado traz impactos técnicos que devem ser ponderados:

#### 5.1 Benefícios

1. **Extensibilidade sem Risco de Regressão:**  
   Novos modelos de negócio (ex.: comissão especial de fim de ano, repasse escalonado por meta ou bônus de fidelidade) são implementados via novas classes isoladas. O código estável da classe `Comissao` não é alterado, anulando o risco de quebrar regras consolidadas.
2. **Alta Testabilidade Unitária:**  
   As regras de cálculo passam a ser funções puras que recebem um valor monetário e retornam outro. Podem ser testadas exaustivamente com dezenas de cenários de borda sem a sobrecarga de instanciar entidades completas ou fixtures de repositório.
3. **Alinhamento ao SRP:**  
   A entidade `Comissao` reassume seu propósito conceitual único: proteger as invariantes do ciclo de vida da remuneração (vincular apenas atendimentos concluídos, consistência de barbeiro e identidade única).

#### 5.2 Custos e Desvantagens

1. **Aumento de Indireção Cognitiva:**  
   No design original com percentual único, a lógica de apuração era compreendida em uma única linha de leitura. Com a aplicação do padrão, há um salto de indireção: o desenvolvedor precisa navegar da entidade até a interface e sua implementação concreta para compreender a regra em execução.
2. **Proliferação de Classes no Módulo de Domínio:**  
   Foram adicionadas quatro classes no arquivo `model.py`. Para sistemas de escopo reduzido em que as regras nunca variam, essa abordagem pode caracterizar *over-engineering* inicial. A complexidade só se justifica quando há variação real ou frequente no domínio.
3. **Adaptação na Serialização da API:**  
   Regras não baseadas em um percentual escalar simples (como a dedução fixa de R$ 5,00 da regra júnior) tornam o campo `percentual` nulo (`None`). A camada de apresentação (`_comissao_para_dict`) teve que ser adaptada para suportar essa variação sem falhar.

#### 5.3 Conclusão da Avaliação

A refatoração justifica-se plenamente a partir do momento em que o negócio demanda diferenciação de cálculo (sênior vs. júnior com insumos). O custo de gerenciar três pequenas classes adicionais é expressivamente menor do que o custo de manter uma cadeia crescente de condicionais dentro da entidade de domínio principal.

---

*Documento revisado e validado. Refatoração e documentação desenvolvidas com auxílio de agente de engenharia de software autônomo.*

## Seção: Marcello Bimbatti Mazzochi - Agregado Agenda

* **Princípio violado:** Princípio Aberto-Fechado.
* **Trecho de código e Hash:** A violação ocorria no método `adicionar_agendamento` da classe `Agenda`. Hash: `0dfb75ae2847f05c3b443471a93b89ee47a0617b`.
* **Problema concreto:** A classe `Agenda` estava responsável por armazenar a coleção de agendamentos e também por definir a regra de conflito de horários. Se houver uma mudança de requisito exigindo que o sistema passe a considerar a `duracao` do serviço para bloquear horários sobrepostos, seríamos obrigados a modificar o código interno da `Agenda`, ferindo o OCP.
* **Refatoração e Hash "depois":** Foi criada uma abstração `RegraDisponibilidade` e uma implementação concreta `ValidadorHorarioExato`. A classe `Agenda` passou a receber o validador via injeção de dependência. Hash do commit: `9e4fea2911b43eeda771d4ba603be05efbd4dddc`.
* **Garantia dos testes:** A assinatura original foi mantida instanciando o `ValidadorHorarioExato` como valor padrão no construtor da `Agenda`. Isso garantiu que todos os testes unitários originais de conflito e agendamento continuassem passando sem alteração de comportamento.
* **Custo da refatoração:** Mais classes e uma indireção no construtor da Agenda. O custo compensa pois agora o sistema suporta novas políticas de agendamento (tolerância de atraso, sobreposição ou cálculo de duração de serviço) criando novas classes de validação, sem tocar na estrutura de dados da `Agenda`.

## Seção: Jonathan do Nascimento Melo — Agregado Barbeiro

---

### 1. Princípio Escolhido

**SRP — Princípio da Responsabilidade Única** (*Single Responsibility Principle*)

> "Uma classe deve ter um, e somente um, motivo para mudar."
> — Robert C. Martin

---

### 2. Identificação da Violação (código anterior a 06/10)

#### 2.1 O Código Original

No commit `f30f823` (29/09/2026), a classe `barbeiro` era responsável por duas coisas ao mesmo tempo: guardar os dados do profissional (nome, id, agendamentos) **e** conter toda a lógica de expediente — quais dias ele trabalha, horário de início e fim, se um determinado horário cabe dentro do turno, e levantar exceção quando não cabe.

```python
# model.py — ANTES da refatoração (commit f30f823)
class barbeiro:
    def __init__(self, id, nome, horario_inicio="08:00", horario_fim="18:00",
                 dias_trabalho="0,1,2,3,4,5"):
        self.id = id
        self.nome = nome
        self.horario_inicio = horario_inicio
        self.horario_fim = horario_fim
        self.dias_trabalho = dias_trabalho

    def _obter_dias_trabalho(self):
        # parsing de string "0,1,2,3,4,5" dentro da entidade
        ...

    def pode_atender(self, data_hora, duracao_minutos: int = 0) -> bool:
        # ~25 linhas de lógica de calendário dentro da entidade
        ...

    def validar_agendamento(self, data_hora, duracao_minutos: int = 0):
        # ~20 linhas de lógica de calendário dentro da entidade
        ...
```

#### 2.2 O Problema Concreto

A classe tinha **dois motivos independentes para mudar**:

| Motivo de mudança | Exemplo concreto |
|---|---|
| **Dados do barbeiro** | Adicionar campo `especialidade`, mudar como a igualdade por `id` funciona. |
| **Regras de expediente** | Adicionar tolerância de 5 minutos no início, suportar jornada noturna com virada de meia-noite, aceitar dias por nome em vez de número. |

Qualquer ajuste numa regra de horário obrigava a abrir a classe `barbeiro` — a entidade central do agregado — correndo o risco de introduzir bugs em código que não tinha nada a ver com aquela mudança.

Além disso, os três atributos de jornada (`horario_inicio`, `horario_fim`, `dias_trabalho`) ficavam soltos no objeto sem nenhuma garantia de coerência. Um trecho de código poderia alterar `horario_inicio` sem tocar em `horario_fim` e o barbeiro ficaria com expediente sem sentido, sem nenhum erro em tempo de execução.

---

### 3. A Refatoração — SRP aplicado ao Barbeiro

#### 3.1 Hashes Git

| Marco | Hash |
|---|---|
| Último commit com a violação (antes) | `f30f823` |
| Commit que introduz a refatoração (SRP) | `dd39e94` |
| Commit com testes unitários do SRP | `adddd3e` |

#### 3.2 Solução: Value Object `JornadaTrabalho`

A ideia foi simples: tirar tudo que é "regra de calendário" da classe `barbeiro` e colocar num objeto próprio, imutável, que só existe para isso.

Criei o `JornadaTrabalho` como um `@dataclass(frozen=True)` — o `frozen` garante que ninguém consegue alterar um campo isolado; se quiser mudar o expediente, precisa criar um objeto novo inteiro.

```python
# model.py — DEPOIS da refatoração
@dataclass(frozen=True)
class JornadaTrabalho:
    horario_inicio: str = "08:00"
    horario_fim: str = "18:00"
    dias_trabalho: str = "0,1,2,3,4,5"

    def obter_dias(self) -> list[int]: ...
    def contem_dia(self, data_hora) -> bool: ...
    def contem_horario(self, data_hora, duracao_minutos=0) -> bool: ...
    def validar_atendimento(self, data_hora, duracao_minutos=0) -> None: ...
    def com_novo_expediente(self, novo_inicio, novo_fim) -> "JornadaTrabalho": ...


class barbeiro:
    def __init__(self, id, nome, horario_inicio="08:00", horario_fim="18:00",
                 dias_trabalho="0,1,2,3,4,5", jornada: JornadaTrabalho | None = None):
        self.id = id
        self.nome = nome
        # jornada calculada como propriedade para manter compatibilidade com ORM
        ...

    def pode_atender(self, data_hora, duracao_minutos=0) -> bool:
        return self.jornada.contem_horario(data_hora, duracao_minutos)  # delega

    def validar_agendamento(self, data_hora, duracao_minutos=0):
        self.jornada.validar_atendimento(data_hora, duracao_minutos)    # delega
```

Depois da refatoração, `barbeiro` tem uma responsabilidade: identidade e agendamentos. `JornadaTrabalho` tem uma responsabilidade: regras de expediente. Cada um muda por um motivo diferente.

**Decisão sobre o SQLAlchemy:** O mapeamento imperativo hidrata objetos sem chamar `__init__`, então precisei manter os atributos escalares (`horario_inicio`, `horario_fim`, `dias_trabalho`) no `barbeiro` para o ORM continuar funcionando. A propriedade `jornada` constrói e sincroniza o `JornadaTrabalho` a partir dessas colunas sempre que precisa. Não quebrei nenhum teste de integração nem precisei mexer no banco.

---

### 4. Garantia dos Testes

| Arquivo | Antes | Depois | O que cobre |
|---|---|---|---|
| `tests/unit/test_barbeiro.py` | 12 testes | **16 testes** | 4 novos testes do `JornadaTrabalho` isolado + integração com `barbeiro` |

Testes novos que comprovam a refatoração:

- `test_jornada_trabalho_isolada_value_object` — testa `obter_dias`, `contem_dia`, `contem_horario` e `validar_atendimento` **sem criar nenhum `barbeiro`**. Prova que `JornadaTrabalho` funciona sozinho.
- `test_jornada_trabalho_com_novo_expediente_imutavel` — confirma que `com_novo_expediente` retorna um objeto novo sem alterar o original. O `frozen=True` impede modificação direta.
- `test_barbeiro_com_jornada_injetada_srp` — cria um `JornadaTrabalho` separado, injeta no construtor de `barbeiro` e verifica que a delegação funciona corretamente.
- `test_barbeiro_definir_nova_jornada_dinamica` — chama `barbeiro.definir_jornada(nova)` e confirma que `horario_inicio` e `horario_fim` do barbeiro ficam sincronizados.

Todos os **104 testes do projeto continuam passando**, nenhuma regressão.

---

### 5. Custo x Benefício

#### O que melhorou

- **Cada classe tem um dono claro.** Se alguém precisar mudar a regra de horário no futuro, abre `JornadaTrabalho` e não precisa nem olhar para o resto do `barbeiro`.
- **Testar regras de expediente ficou fácil.** Não precisa montar agendamentos, serviços ou repositórios — só cria um `JornadaTrabalho` e testa direto.
- **Nenhum estado inconsistente.** O `frozen=True` garante que início, fim e dias sempre andam juntos.

#### O que ficou mais complexo

- **A propriedade `jornada` com sincronização bidirecional existe só por causa do ORM.** Sem o SQLAlchemy imperativo, não precisaria disso. É um custo que vem da infraestrutura, não do domínio.
- **O setter precisa manter três atributos sincronizados.** Se a jornada ganhar um novo campo no futuro, o setter precisa ser atualizado também.
- **Mais uma classe no `model.py` compartilhado.** Idealmente ficaria num módulo só do agregado `barbeiro`, mas como o projeto usa um único `model.py` para tudo, ela fica lá por enquanto.

No geral, valeu a pena. A classe `barbeiro` ficou mais limpa, os testes de expediente ficaram independentes e qualquer ajuste nas regras de horário agora é feito num lugar só, sem risco de quebrar agendamentos.

---

*Feito por Jonathan do Nascimento Melo. Usei um assistente de IA para ajudar a estruturar o código e redigir a documentação. O código foi testado e os commits foram feitos por mim.*
