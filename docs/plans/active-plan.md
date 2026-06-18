# Plano ativo — Confiabilidade da base

## Objetivo

Eliminar o risco de perda involuntária de transações e estabelecer uma validação automatizada e reproduzível para backend e frontend.

## Entrega 1 — Integridade na exclusão de recursos

Alterar os relacionamentos do SQLAlchemy para que excluir uma conta não exclua suas transações. Aplicar e validar a mesma regra de preservação para cartões e faturas: o recurso financeiro é removido e a referência correspondente da transação passa a ser nula.

Critérios de aceite:

- excluir uma conta preserva as transações associadas;
- excluir um cartão preserva suas transações e remove suas faturas conforme a regra atual;
- excluir uma fatura preserva as transações associadas;
- testes de regressão comprovam os três comportamentos.

## Entrega 2 — Testes com PostgreSQL

Criar uma camada de testes de integração contra PostgreSQL para validar comportamento de chaves estrangeiras, índices parciais e tipos específicos que o SQLite não reproduz.

Critérios de aceite:

- os testes criam dados isolados e não dependem do seed de desenvolvimento;
- exclusões e detecção de transações duplicadas são verificadas no PostgreSQL;
- a suíte pode ser executada por um único comando via Docker Compose;
- dados de teste são descartados ao final da execução.

## Entrega 3 — Integração contínua

Adicionar um workflow para validar backend e frontend em mudanças enviadas ao repositório.

Critérios de aceite:

- o backend executa toda a suíte com PostgreSQL disponível;
- o frontend executa lint, typecheck e build de produção;
- qualquer falha encerra o workflow com status de erro;
- o workflow não depende de credenciais externas nem da Pluggy.

## Entrega 4 — Experiência de desenvolvimento consistente

Revisar os comandos documentados e o `Makefile` para que o caminho principal seja Docker, evitando dependência de uma `.venv` criada em outro sistema operacional.

Critérios de aceite:

- os comandos principais funcionam no Windows com GNU Make e em ambientes Unix;
- há comandos claros para subir, descer, consultar logs e executar testes;
- o README aponta para um único fluxo recomendado de inicialização;
- nenhum ambiente virtual local é necessário para o fluxo Docker.

## Ordem de execução

As entregas devem ser implementadas na ordem apresentada. A primeira corrige o risco funcional; a segunda comprova o comportamento no banco real; a terceira automatiza essa proteção; a quarta reduz diferenças entre máquinas.

## Fora desta entrega

CRUD completo de transações no frontend, paginação, reforço do Agent Gateway, backup e integração Pluggy permanecem no roadmap e não fazem parte deste plano ativo.
