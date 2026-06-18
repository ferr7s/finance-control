# Roadmap do Finance Control

Este documento registra a direção do produto. Ele descreve a ordem recomendada das entregas, sem funcionar como controle diário de tarefas.

## Estado atual

O MVP já oferece:

- dashboard financeiro com fluxo mensal, patrimônio, categorias, recorrências e faturas;
- cadastro de contas, cartões e faturas;
- consulta e categorização de transações;
- importação CSV com pré-visualização e detecção de duplicidades;
- insights locais;
- Agent Gateway REST e servidor MCP;
- execução local com Docker Compose, PostgreSQL, FastAPI e Next.js.

## Fase 1 — Confiabilidade da base

Objetivo: proteger os dados e tornar cada mudança verificável antes de ampliar as funcionalidades.

- preservar transações quando contas, cartões ou faturas forem removidos;
- cobrir regras de integridade e exclusão com testes;
- executar testes de integração usando PostgreSQL;
- automatizar testes, lint, typecheck e build no CI;
- alinhar comandos de desenvolvimento entre Windows, Linux e Docker.

## Fase 2 — Gestão completa de transações

Objetivo: permitir que todo o ciclo de manutenção financeira seja concluído pela interface.

- criar, editar e excluir transações manualmente;
- associar transações a contas, cartões e faturas;
- adicionar paginação à API e à interface;
- melhorar revisão e tratamento de duplicidades na importação;
- criar testes de ponta a ponta para o fluxo de importação até o dashboard.

## Fase 3 — Segurança e operação

Objetivo: preparar a aplicação para uso contínuo sem depender de configurações inseguras de desenvolvimento.

- remover credenciais fixas da interface e dos exemplos executáveis;
- separar configurações de desenvolvimento e produção;
- limitar arquivos enviados e validar entradas nas fronteiras da aplicação;
- implementar exportação, backup e restauração dos dados;
- adicionar logs operacionais para importações e integrações.

## Fase 4 — Integrações financeiras

Objetivo: conectar fontes externas somente depois que integridade, testes e operação estiverem consolidados.

- substituir o stub da Pluggy por autenticação real;
- sincronizar contas, cartões, faturas e transações de forma idempotente;
- registrar histórico e falhas de sincronização;
- permitir reconciliação entre dados importados manualmente e dados sincronizados.

## Critério de priorização

Integridade de dados vem antes de conveniência; automação de qualidade vem antes de novas integrações; funcionalidades externas não devem avançar enquanto a base local não estiver recuperável e testada.
