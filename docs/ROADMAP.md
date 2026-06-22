# Roadmap do Finance Control

Este documento registra a direção do produto. Ele descreve a ordem recomendada das entregas, sem funcionar como controle diário de tarefas.

## Estado atual

O MVP já oferece:

- dashboard financeiro com fluxo mensal, patrimônio, categorias, recorrências e faturas;
- cadastro manual de contas bancárias, cartões de crédito e faturas;
- consulta e categorização de transações (somente leitura — sem importação CSV);
- insights locais;
- Agent Gateway REST e servidor MCP;
- execução local com Docker Compose, PostgreSQL, FastAPI e Next.js;
- seed de demonstração disponível via `make seed` (não roda automaticamente).

## Fase 1 — Confiabilidade da base ✓ concluída

Objetivo: proteger os dados e tornar cada mudança verificável antes de ampliar as funcionalidades.

## Fase 1 — Confiabilidade da base

Objetivo: proteger os dados e tornar cada mudança verificável antes de ampliar as funcionalidades.

- preservar transações quando contas, cartões ou faturas forem removidos;
- cobrir regras de integridade e exclusão com testes;
- executar testes de integração usando PostgreSQL;
- automatizar testes, lint, typecheck e build no CI;
- alinhar comandos de desenvolvimento entre Windows, Linux e Docker.

## Fase 2 — Integrações financeiras (próxima)

Objetivo: conectar fontes externas para sincronização automática de contas e transações.

- substituir o stub da Pluggy por autenticação real (item/connect token);
- sincronizar contas, cartões, faturas e transações de forma idempotente;
- registrar histórico e falhas de sincronização;
- permitir reconciliação entre dados manuais e dados sincronizados.

## Fase 3 — Segurança e operação

Objetivo: preparar a aplicação para uso contínuo sem depender de configurações inseguras de desenvolvimento.

- remover credenciais fixas da interface e dos exemplos executáveis;
- separar configurações de desenvolvimento e produção;
- implementar exportação, backup e restauração dos dados;
- adicionar logs operacionais para sincronizações e integrações.

## Critério de priorização

Integridade de dados vem antes de conveniência; automação de qualidade vem antes de novas integrações; funcionalidades externas não devem avançar enquanto a base local não estiver recuperável e testada.
