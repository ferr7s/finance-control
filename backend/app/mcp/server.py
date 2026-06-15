from mcp.server.fastmcp import FastMCP

from backend.app.mcp import tools

mcp = FastMCP("finance-control")


@mcp.tool()
async def get_dashboard_summary():
    return await tools.get_dashboard_summary()


@mcp.tool()
async def search_transactions(
    query: str | None = None,
    category: str | None = None,
    provider: str | None = None,
    type: str | None = None,
    limit: int = 50,
):
    return await tools.search_transactions(query=query, category=category, provider=provider, type=type, limit=limit)


@mcp.tool()
async def get_category_breakdown():
    return await tools.get_category_breakdown()


@mcp.tool()
async def get_monthly_cashflow():
    return await tools.get_monthly_cashflow()


@mcp.tool()
async def get_recurring_expenses():
    return await tools.get_recurring_expenses()


@mcp.tool()
async def get_credit_card_summary():
    return await tools.get_credit_card_summary()


@mcp.tool()
async def get_net_worth():
    return await tools.get_net_worth()


@mcp.tool()
async def generate_financial_context():
    return await tools.generate_financial_context()


@mcp.tool()
async def save_agent_analysis(source: str, title: str, content: str, metadata: dict | None = None):
    return await tools.save_agent_analysis(source=source, title=title, content=content, metadata=metadata)


if __name__ == "__main__":
    mcp.run()
