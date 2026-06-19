# Plano ativo — Remoção das entradas financeiras manuais

## Objetivo

Transformar a aplicação em somente leitura até a integração Open Finance. Contas, cartões, faturas e transações continuarão visíveis, mas não poderão ser criados, editados, excluídos ou importados manualmente. Nenhum dado existente deve ser removido.

## Entrega 1 — Interface financeira somente leitura

Remover formulários e ações de escrita das páginas financeiras, preservando consultas, filtros e visualizações.

Critérios de aceite:

- contas existentes são exibidas sem formulário ou ações de edição e exclusão;
- cartões e faturas existentes são exibidos sem formulários ou ações de edição e exclusão;
- transações existentes são exibidas sem edição manual de categoria;
- a importação CSV é removida da interface;
- estados vazios informam que os dados serão obtidos pela futura conexão bancária;
- o cliente frontend não expõe métodos ou tipos de escrita financeira sem uso.

## Entrega 2 — API financeira pública somente leitura

Remover da API pública as operações manuais de escrita, mantendo os serviços internos necessários para a futura sincronização Open Finance.

Critérios de aceite:

- contas, cartões, faturas e transações mantêm seus endpoints `GET`;
- endpoints públicos `POST`, `PATCH` e `DELETE` desses recursos são removidos;
- `/api/import/bank-csv` e `/api/import/bank-csv/preview` deixam de existir;
- parser, serviço, testes e dependência usados exclusivamente pela importação CSV são removidos;
- geração de insights e armazenamento de análises textuais continuam funcionando;
- o OpenAPI não publica operações financeiras de escrita.

## Entrega 3 — Seed opcional e preservação dos dados

Impedir que dados fictícios sejam criados automaticamente sem retirar a opção explícita de demonstração.

Critérios de aceite:

- o backend não executa `seed.py` durante a inicialização normal;
- `make seed` continua disponível como ação explícita;
- instalações novas podem iniciar com banco vazio;
- nenhuma migration ou rotina remove dados existentes.

## Entrega 4 — Testes e documentação

Adaptar a validação automatizada ao contrato somente leitura e registrar a nova direção do produto.

Critérios de aceite:

- testes preparam dados por fixtures, ORM ou serviços internos, sem usar rotas públicas removidas;
- consultas financeiras e regras internas de integridade continuam cobertas;
- testes comprovam a ausência das rotas de escrita e importação CSV;
- backend, lint, typecheck e build do frontend passam;
- README, roadmap e handoff descrevem a aplicação somente leitura e o seed opcional.

## Ordem de execução

1. Criar uma branch curta a partir de `main`.
2. Implementar a interface somente leitura.
3. Remover as rotas públicas de escrita e todo o fluxo CSV.
4. Tornar o seed opcional.
5. Adaptar os testes e executar `make check`.
6. Atualizar a documentação e revisar o diff completo.

## Decisões fixadas

- remover toda entrada manual, incluindo importação CSV;
- remover também os endpoints públicos de escrita financeira;
- manter serviços internos de persistência para a futura integração bancária;
- preservar todos os dados existentes;
- manter páginas financeiras visíveis em modo somente leitura;
- manter `make seed` apenas para uso explícito;
- não implementar a conexão bancária neste plano.

## Próxima fase

Depois desta entrega, definir e implementar a sincronização automática de contas, cartões, faturas e transações via Open Finance, usando a estrutura Pluggy existente como ponto de partida.
