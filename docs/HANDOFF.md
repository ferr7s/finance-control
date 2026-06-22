# Handoff do projeto

Este arquivo é o ponto de entrada para continuar o trabalho em outra máquina ou em uma nova sessão.

## Referência atual

- Data da referência: 2026-06-22
- Branch: `main`
- Commit: ver `git log --oneline -1`
- Plano ativo: nenhum — plano de limpeza pré-Open Finance concluído
- Direção do produto: [Roadmap](ROADMAP.md)

## Estado da plataforma

- O frontend usa Next.js e está exposto na porta `3000`.
- O backend usa FastAPI e está exposto na porta `8000`.
- O PostgreSQL está exposto na porta `5432`.
- Docker Compose inicializa banco, migrations, backend e frontend. **O seed não roda automaticamente.**
- Contas bancárias, cartões e faturas têm CRUD completo pela interface.
- Transações são somente leitura: visualização com filtros e edição de categoria. Importação CSV foi removida.
- A fase de confiabilidade da base foi concluída no PR #7.

## Foco atual

Implementar a integração Open Finance via Pluggy: autenticação real, sincronização idempotente de contas e transações, histórico de sincronizações.

## Como retomar

1. Confirmar que o repositório local está na branch `main` atualizada.
2. Ler o [Roadmap](ROADMAP.md) para entender a próxima fase.
3. Executar `make up` para subir o ambiente.
4. Criar uma branch curta a partir de `main`.

## Arquivos centrais para a próxima entrega (Open Finance)

- `backend/app/services/pluggy_service.py` — stub atual da integração Pluggy
- `backend/app/api/routes/` — local para as rotas de sincronização
- `backend/app/models/` — modelos de Account, Transaction, CreditCard

## Comandos úteis

```bash
make up          # sobe toda a aplicação
make down        # encerra containers
make seed        # carrega dados de demonstração (ação explícita)
make test        # testes do backend
make frontend-check  # lint, typecheck e build do frontend
make check       # testes + verificações completas
```

## Restrições vigentes

- manter a aplicação local-first;
- não adicionar operações financeiras como pagamentos, Pix ou transferências;
- não integrar LLMs ao backend;
- manter ferramentas financeiras dos agentes em modo somente leitura, exceto pelo armazenamento de análises textuais.
