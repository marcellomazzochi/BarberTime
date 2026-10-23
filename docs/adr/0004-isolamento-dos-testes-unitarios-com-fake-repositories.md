# ADR-0004: Isolamento dos testes unitários com Fake Repositories

| Campo | Valor |
|---|---|
| **Status** | Aceita |
| **Data** | 2026-10-22 |
| **Autor** | Johnny Godoy |



## Contexto

O BarberTime utiliza repositórios para separar as regras de negócio da persistência. Os serviços recebem repositórios por injeção de dependência, permitindo utilizar implementações SQLAlchemy na aplicação e implementações Fake nos testes.

O projeto precisa validar suas regras de negócio sem exigir banco de dados, sessão SQLAlchemy ou servidor Flask durante a execução dos testes unitários. Ao mesmo tempo, os testes precisam detectar problemas reais de persistência.

## Alternativas consideradas

### Alternativa 1: Utilizar Fake Repositories nos testes unitários

**Vantagens:**
- Permite testar regras de negócio sem banco de dados.
- Facilita isolar falhas nos serviços.
- Favorece a execução rápida da suíte unitária.

**Desvantagens:**
- Exige manter os fakes consistentes com os contratos dos repositórios reais.
- Não identifica sozinho erros de mapeamento ORM ou persistência.

### Alternativa 2: Utilizar o SQLAlchemy diretamente em todos os testes

**Vantagens:**
- Exercita a persistência real.
- Pode detectar erros de mapeamento e consulta.

**Desvantagens:**
- Aumenta a dependência de infraestrutura nos testes unitários.
- Dificulta distinguir erros de domínio de problemas de persistência.
- Pode aumentar o tempo de execução da suíte.

## Decisão proposta

Manter Fake Repositories nos testes unitários dos serviços e utilizar os repositórios SQLAlchemy nos testes de integração. Os testes de ponta a ponta continuarão verificando o comportamento da API Flask.

## Consequências

**Positivas:**
- Regras de negócio podem ser testadas sem infraestrutura externa.
- Testes de integração verificam o comportamento real da persistência.
- Falhas podem ser localizadas com mais facilidade conforme o nível de teste.

**Negativas:**
- Os fakes precisam acompanhar os contratos dos repositórios.
- A aprovação dos testes unitários não garante que o mapeamento ORM esteja correto.

## Verificação

Executar `pytest tests/unit/` sem banco, sessão SQLAlchemy ou servidor Flask. Executar separadamente os testes de integração com SQLite em memória e os testes de API.

A meta de desempenho dos testes unitários deverá ser verificada conforme o cenário definido na Seção 2 de `docs/arquitetura.md`.
