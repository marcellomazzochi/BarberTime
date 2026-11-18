# Retrospectiva Arquitetural — BarberTime

> **Questão central:** *Depois de conviver com a arquitetura baseada em Ports & Adapters, Repository e Service Layer ao longo de toda a Fase 2 (documentando trade-offs, refatorando SOLID e aplicando padrões GoF), nós a escolheríamos de novo para o domínio da barbearia?*

---

## 1. Revisão da Análise do Checkpoint 1: As Previsões se Confirmaram?

No Checkpoint 1, documentamos no [docs/arquitetura.md](file:///c:/Users/jonat/OneDrive/Desktop/BarberTime/docs/arquitetura.md) e no [ADR 0002](file:///c:/Users/jonat/OneDrive/Desktop/BarberTime/docs/adr/0002-mapeamento-imperativo-com-sqlalchemy-para-preservar-dominio-puro.md) que a adoção da arquitetura limpa em camadas traria alta testabilidade e independência tecnológica, ao custo de maior verbosidade e sobrecarga estrutural inicial.

### 1.1 O que se confirmou com louvor: Testabilidade e Estabilidade
* **Velocidade da suíte de testes:** A previsão de que testes sem dependência de banco de dados rodariam em tempo quase nulo se confirmou integralmente. A suíte completa do projeto saltou de poucas dezenas de testes na Fase 1 para **129 testes automatizados na Fase 2**, e roda integralmente em **0,93 segundos**.
* **Zero acoplamento com o framework web:** Durante toda a evolução do sistema, as alterações em regras de agendamento e comissões foram conduzidas sem tocar em rotas do Flask.
* **Segurança nas refatorações:** A existência dos `FakeRepository` permitiu refatorar regras centrais de negócio com respostas instantâneas no terminal, servindo como uma rede de segurança sólida.

### 1.2 O que pesou mais na prática: O custo da indireção e a rigidez do mapeamento
* **Proliferação de arquivos para mudanças triviais:** Para expor qualquer nova funcionalidade (como consultar o status operacional do barbeiro), foi necessário navegar e alterar até cinco arquivos distintos: `model.py` (domínio), `orm.py` (mapeamento relacional), `repository.py` (interface e SQL), `services.py` (orquestração) e `flask_app.py` (apresentação HTTP).
* **Camadas intermediárias passivas (*Middle Man*):** Em operações puramente cadastrais de consulta (como `listar_barbeiros`), a camada de serviço limitou-se a chamar `repo.list()`, atuando como mero intermediário sem agregar valor de negócio real.

---

## 2. Evidências da Fase 2: As Camadas Facilitaram ou Atrapalharam?

A convivência diária com o código durante os Checkpoints 2 e 3 gerou evidências empíricas concretas sobre os limites e virtudes dessa arquitetura:

### 2.1 Onde as camadas facilitaram expressivamente
1. **Refatoração SOLID no Agregado Barbeiro (Checkpoint 2):**  
   Quando extraímos o Value Object imutável `JornadaTrabalho` da classe `barbeiro` para sanar a violação de SRP (commit `dd39e94`), o fato de `model.py` ser Python puro permitiu criar o dataclass com `@dataclass(frozen=True)` e testar sua imutabilidade e métodos de cálculo de calendário de forma 100% isolada em `test_barbeiro.py`, sem abrir conexão SQLite.
2. **Aplicação do Padrão GoF State no Barbeiro (Checkpoint 3):**  
   A introdução do padrão GoF State (commits `c16b32f` e `aacb622`) permitiu modelar o ciclo de vida do barbeiro (`DISPONIVEL`, `EM_FERIAS`, `EM_PAUSA`, `INATIVO`) através de polimorfismo puro. O `FakeBarbeiroRepository` possibilitou validar todas as transições de estado e o bloqueio de agendamentos na camada de serviço sem depender de commits em banco de dados.
3. **Padrão Decorator na Comissão (Checkpoint 3):**  
   O desacoplamento entre o cálculo de repasse e a entidade `Comissao` permitiu empilhar bônus e taxas dinâmicas em tempo de execução sem alterar uma única linha da entidade principal.

### 2.2 Onde as camadas geraram atrito e complexidade desnecessária
1. **A fricção do Mapeamento Imperativo clássico do SQLAlchemy:**  
   O SQLAlchemy clássico (`map_imperatively`) hidrata objetos recuperados do banco alocando diretamente seus atributos de classe, **sem executar o construtor `__init__`**.  
   *Consequência concreta no código:* Na refatoração do Barbeiro, fomos forçados a manter atributos escalares redundantes (`horario_inicio`, `horario_fim`, `dias_trabalho`) e criar uma propriedade `jornada` com sincronização bidirecional em tempo de execução. Esse código defensivo existiu unicamente para contornar limitações do ORM, e não por necessidade do negócio.
2. **Esforço desproporcional para operações simples:**  
   Em agregados com poucas regras de negócio (como a consulta simples de histórico), manter interfaces abstratas de repositório, repositório fake e repositório real de SQLAlchemy triplicou o volume de código sem ganho proporcional de manutenibilidade.

---

## 3. Decisão Final Justificada: Manter, Trocar ou Híbrida?

### A Decisão: Adotar uma Solução Híbrida Pragmática (*Pragmatic Clean Architecture*)

Se tivéssemos que recomeçar o projeto hoje para um ambiente de produção real de barbearia, **não escolheríamos nem o modelo atual em sua forma mais estrita, nem um monolito Active Record (estilo Django)**. Escolheríamos uma **abordagem híbrida pragmática**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ARQUITETURA HÍBRIDA                             │
├───────────────────────────────────┬────────────────────────────────────┤
│         FLUXO DE COMANDOS         │         FLUXO DE CONSULTAS         │
│     (Gravações / Regras Ricas)    │         (Leituras Simples)         │
├───────────────────────────────────┼────────────────────────────────────┤
│ • Domínio Puro com Padrões GoF    │ • Query Direta ao Banco            │
│   (State, Strategy, Decorator)    │ • Sem passar por Repositório/DTO   │
│ • Service Layer orquestrando      │ • Menor latência e sem boilerplate │
│ • Mapeamento Declarativo Moderno  │ • Alto desempenho para listagens   │
│   (SQLAlchemy 2.0 Mapped)         │                                    │
└───────────────────────────────────┴────────────────────────────────────┘
```

### Justificativa da Escolha:

1. **Por que NÃO trocar por Active Record / Django:**  
   O Active Record acopla o modelo de dados à regra de negócio. Perderíamos a capacidade de testar o ciclo de vida do barbeiro em 0,1s, Value Objects como `JornadaTrabalho` seriam achatados em colunas soltas e a aplicação de padrões comportamentais como State e Decorator seria dificultada pelas amarras do ORM. A segurança e clareza conquistadas na Fase 2 seriam perdidas.

2. **Por que NÃO manter o modelo atual 100% estrito:**  
   O mapeamento imperativo clássico (`map_imperatively`) adiciona uma sobrecarga de manutenção que já não se justifica no Python moderno. Além disso, criar Repositório e Service Layer para simples consultas de leitura é um desperdício de produtividade.

3. **O que a Solução Híbrida propõe:**
   - **Modernização do ORM com SQLAlchemy 2.0 Declarativo:** Usar `Mapped` e `mapped_column` com Dataclasses nativas do Python. As entidades continuam limpas, mas eliminamos as centenas de linhas de código em `orm.py` e os conflitos de hidratação de atributos.
   - **CQRS Simples:** Manter Service Layer e Repositórios estritos apenas para operações de escrita que alteram estado e protegem invariantes (`cadastrar_barbeiro`, `alterar_status_barbeiro`, `gerar_comissao`). Para operações de leitura (`listar_barbeiros`, `consultar_historico`), permitir queries diretas mais simples e expressivas.

### Conclusão
A jornada da Fase 2 comprovou que a separação de responsabilidades não é um dogma binário (fazer tudo puro vs fazer tudo acoplado), mas um equilíbrio contínuo de trade-offs. A arquitetura em camadas nos protegeu de falhas e viabilizou um software modular e bem testado; a maturidade como engenheiros de software reside em saber onde o isolamento salva o projeto e onde a simplicidade deve prevalecer.
