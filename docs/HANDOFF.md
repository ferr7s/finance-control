# Handoff do projeto

Este arquivo é o ponto de entrada para continuar o trabalho em outra máquina ou em uma nova sessão.

## Referência atual

- Data da referência: 2026-06-19
- Branch: `main`
- Commit: `57130d8`
- Plano em execução: [Remoção das entradas financeiras manuais](plans/active-plan.md)
- Direção do produto: [Roadmap](ROADMAP.md)

## Estado da plataforma

- O frontend usa Next.js e está exposto na porta `3000`.
- O backend usa FastAPI e está exposto na porta `8000`.
- O PostgreSQL está exposto na porta `5432`.
- Docker Compose atualmente inicializa banco, migrations, seed, backend e frontend.
- A interface ainda permite cadastros manuais de contas, cartões e faturas, edição de categoria e importação CSV.
- A fase de confiabilidade da base foi concluída no PR #7.

## Foco atual

Remover todas as entradas financeiras manuais e tornar a aplicação somente leitura antes de iniciar a integração Open Finance. Os dados existentes devem ser preservados e o seed deve deixar de rodar automaticamente.

## Como retomar

1. Confirmar que o repositório local está na branch e no commit indicados acima.
2. Ler `docs/plans/active-plan.md` por completo.
3. Executar `git status` antes de alterar arquivos.
4. Criar uma branch curta a partir de `main`.
5. Iniciar pela Entrega 1: interface financeira somente leitura.

## Arquivos centrais para a próxima entrega

- `frontend/components/net-worth/accounts-manager.tsx`
- `frontend/components/cards/cards-manager.tsx`
- `frontend/components/transactions/transactions-table.tsx`
- `frontend/components/transactions/upload-csv-card.tsx`
- `frontend/lib/api.ts`

## Comandos úteis

```powershell
make up
make down
make status
make test
make frontend-check
make check
```

## Restrições vigentes

- manter a aplicação local-first;
- não apagar dados existentes durante esta entrega;
- não adicionar operações financeiras como pagamentos, Pix ou transferências;
- não integrar LLMs ao backend;
- manter ferramentas financeiras dos agentes em modo somente leitura, exceto pelo armazenamento de análises textuais;
- não implementar a integração Pluggy antes de concluir o plano ativo.
