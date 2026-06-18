# Handoff do projeto

Este arquivo é o ponto de entrada para continuar o trabalho em outra máquina ou em uma nova sessão.

## Referência atual

- Data da referência: 2026-06-18
- Branch: `main`
- Commit: `81cbacd`
- Plano em execução: [Confiabilidade da base](plans/active-plan.md)
- Direção do produto: [Roadmap](ROADMAP.md)

## Estado da plataforma

- O frontend usa Next.js e está exposto na porta `3000`.
- O backend usa FastAPI e está exposto na porta `8000`.
- O PostgreSQL está exposto na porta `5432`.
- Docker Compose inicializa banco, migrations, seed, backend e frontend.
- O MVP contém dashboard, contas, cartões, faturas, transações, importação CSV, insights, Agent Gateway e MCP.

## Foco atual

A próxima entrega é a preservação de transações durante a exclusão de contas, cartões e faturas. O comportamento deve ser definido por testes antes da alteração dos relacionamentos ORM.

## Como retomar

1. Confirmar que o repositório local está na branch indicada acima.
2. Ler `docs/plans/active-plan.md` para entender a ordem e os critérios de aceite.
3. Inspecionar o estado atual com `git status` antes de alterar arquivos.
4. Iniciar pela primeira entrega do plano ativo.

## Arquivos centrais para a próxima entrega

- `backend/app/models/account.py`
- `backend/app/models/credit_card.py`
- `backend/app/models/credit_card_bill.py`
- `backend/app/models/transaction.py`
- `backend/tests/test_financial_resources_api.py`

## Comandos úteis

```powershell
make up
make down
docker compose ps
docker compose run --rm backend pytest -q
cd frontend
npm run lint
npm run typecheck
npm run build
```

## Restrições vigentes

- manter a aplicação local-first;
- não adicionar operações financeiras como pagamentos, Pix ou transferências;
- não integrar LLMs ao backend;
- manter ferramentas financeiras dos agentes em modo somente leitura, exceto pelo armazenamento de análises textuais;
- não iniciar a integração Pluggy antes de concluir a fase de confiabilidade.
