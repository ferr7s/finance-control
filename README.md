# Finance Control

Finance Control é uma aplicação web pessoal local-first para centralizar dados bancários, importar transações, visualizar dashboards financeiros e expor ferramentas seguras para agentes externos por REST e MCP.

O MVP não usa OpenAI API, não executa chamadas para LLM, não faz scraping bancário, não armazena senha de banco e não implementa Pix, pagamentos, transferências, ordens de investimento ou qualquer ação financeira.

## Arquitetura

- `frontend/`: Next.js App Router, TypeScript, Tailwind CSS, componentes shadcn-style e Recharts.
- `backend/`: FastAPI, SQLAlchemy 2.x, Pydantic, Alembic, PostgreSQL, importação CSV, serviços financeiros, Agent Gateway e MCP.
- `postgres`: banco local com contas, cartões, faturas, transações, insights e análises automáticas recebidas de agentes externos.

## Início rápido

O fluxo recomendado usa Docker para banco, backend, frontend, migrations e testes. Instale Docker Desktop (Windows/macOS) ou Docker Engine com o plugin Compose (Linux) e GNU Make.

```bash
make up
```

Sem GNU Make, use `docker compose -p finance-control up --build`.

Depois acesse:

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

O backend roda migrations e seed automaticamente no startup do container.

## Comandos de desenvolvimento

| Comando | Finalidade |
| --- | --- |
| `make up` | Constrói e inicia toda a aplicação. |
| `make down` | Encerra e remove os containers da aplicação. |
| `make restart` | Reinicia os containers existentes. |
| `make status` | Exibe o estado dos serviços. |
| `make logs` | Acompanha os logs dos serviços. |
| `make migrate` | Executa as migrations no backend. |
| `make seed` | Carrega os dados iniciais idempotentes. |
| `make test` | Executa todos os testes do backend, incluindo PostgreSQL. |
| `make test-integration` | Executa apenas os testes de integração PostgreSQL. |
| `make frontend-check` | Executa instalação limpa, lint, typecheck e build do frontend em Node 20. |
| `make check` | Executa os testes do backend e todas as verificações do frontend. |

O seed é idempotente: se encontrar contas já cadastradas, não duplica os dados.
Os testes PostgreSQL criam um banco temporário com nome único e o removem ao final, sem alterar os dados locais da aplicação.

## Importação CSV bancária

Use a página `Transações` para enviar um arquivo CSV. O importador aceita separadores `,` e `;`, datas `dd/mm/yyyy` e `yyyy-mm-dd`, decimal brasileiro e colunas comuns:

- `date`, `data`
- `description`, `descricao`, `descrição`, `histórico`, `historico`
- `amount`, `valor`
- `type`, `tipo`
- `category`, `categoria`
- `account`, `conta`
- `card`, `cartão`, `cartao`
- `provider`, `banco`, `instituição`, `instituicao`

O retorno informa total de linhas, importadas, ignoradas e erros.

## Agent Gateway REST

Todas as rotas `/api/agent/*` exigem:

```http
Authorization: Bearer dev-local-key
```

Ferramentas disponíveis:

- `GET /api/agent/health`
- `GET /api/agent/dashboard-summary`
- `GET /api/agent/net-worth`
- `GET /api/agent/category-breakdown`
- `GET /api/agent/monthly-cashflow`
- `GET /api/agent/recurring-expenses`
- `GET /api/agent/credit-card-summary`
- `POST /api/agent/transactions/search`
- `POST /api/agent/context/generate`
- `POST /api/agent/analyses`

Somente `POST /api/agent/analyses` grava dados, e grava apenas na tabela `agent_analyses`.

Manifestos:

- http://localhost:8000/agent_tools_manifest.json
- http://localhost:8000/openapi_agent_tools.yaml

## MCP

Exemplo de configuração:

```json
{
  "mcpServers": {
    "finance-control": {
      "command": "python",
      "args": ["-m", "backend.app.mcp.server"],
      "env": {
        "FINANCE_CONTROL_API_URL": "http://localhost:8000",
        "AGENT_API_KEY": "dev-local-key"
      }
    }
  }
}
```

Tools MCP:

- `get_dashboard_summary`
- `search_transactions`
- `get_category_breakdown`
- `get_monthly_cashflow`
- `get_recurring_expenses`
- `get_credit_card_summary`
- `get_net_worth`
- `generate_financial_context`
- `save_agent_analysis`

## Variáveis de ambiente

Veja `.env.example`.

Principais variáveis:

- `DATABASE_URL`
- `BACKEND_CORS_ORIGINS`
- `AGENT_API_KEY`
- `FINANCE_CONTROL_API_URL`
- `PLUGGY_CLIENT_ID`
- `PLUGGY_CLIENT_SECRET`
- `PLUGGY_BASE_URL`

## Pluggy / Open Finance

`backend/app/services/pluggy_service.py` contém um stub funcional para integração futura. Sem credenciais, os métodos retornam erro controlado: `Pluggy não configurado`.

## Restrições de segurança

- Não há scraping de bancos.
- Não há armazenamento de senhas bancárias.
- Não há cripto no MVP.
- Não há endpoints `/api/crypto/*`.
- Não há `OPENAI_API_KEY`.
- Não há chamadas para LLM no backend.
- Agentes externos não podem criar, editar ou apagar transações, contas, cartões ou faturas.
- Agentes externos não podem executar pagamentos, Pix, transferências ou ordens de investimento.

## Planejamento e continuidade

- [Roadmap do produto](docs/ROADMAP.md)
- [Plano técnico ativo](docs/plans/active-plan.md)
- [Ponto de retomada entre máquinas e sessões](docs/HANDOFF.md)
