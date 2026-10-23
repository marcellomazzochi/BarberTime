# ADR 0003 — Agenda impede agendamentos no mesmo horário

| Campo | Valor |
|---|---|
| **Status** | Aceita |
| **Data** | 2026-10-22 |
| **Autor** | Marcello Bimbatti Mazzochi |
| **Tema** | Regra de negócio da Agenda |

---

## Contexto

Impedir que um mesmo barbeiro receba dois agendamentos para o mesmo horário. O projeto atribui essa regra ao agregado Agenda. A implementação está em `src/BarberTime/domain/model.py`. `Agenda` mantém os agendamentos em um dicionário indexado pelo par `(barbeiro, data_hora)` e `adicionar_agendamento` retorna `ValueError` quando a chave já existe. Esse caso está testado em `tests/unit/test_domain.py`.

## Decisão

Manter a verificação de horário na classe `Agenda` antes de registrar o agendamento. A chave considera o barbeiro e o valor de `data_hora`, horários iguais para barbeiros diferentes são permitidos, enquanto dois horários iguais para o mesmo barbeiro não são permitidos.

## Alternativas consideradas

1. Permitir a inclusão e validar apenas na rota ou no banco: A regra ficaria fora do domínio ou dependeria de infraestrutura e seria mais difícil testar isoladamente.
2. Verificar sobreposição de intervalos de atendimento: Exigiria comparar a duração do serviço com outros agendamentos e não apenas comparar o instante de início.
3. Usar identificadores persistentes do barbeiro e armazenar a Agenda no banco: A implementação atual é uma estrutura em memória, sem repositório ou persistência da Agenda.

## Consequências

- A regra é simples de testar sem banco de dados, um teste verifica a inclusão e outro verifica a rejeição de tentar agendar no mesmo horário com o mesmo barbeiro.
- A validação é local na instância `Agenda` e não garante exclusividade entre instâncias ou processos diferentes.
- A comparação considera apenas igualdade exata de `data_hora`. Agendamentos com horários de início diferentes ainda podem ser aceitos.
- Os agendamentos mantidos no dicionário não são persistentes na implementação atual e são perdidos quando a instância deixa de existir. 
