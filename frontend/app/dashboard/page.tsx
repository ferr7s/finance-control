import { AlertCircle, Banknote, CreditCard, Landmark, TrendingDown, TrendingUp, Wallet } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CashflowChart } from "@/components/charts/cashflow-chart";
import { CategoryPieChart } from "@/components/charts/category-pie-chart";
import { NetWorthChart } from "@/components/charts/net-worth-chart";
import { CreditCardSummaryCard } from "@/components/dashboard/credit-card-summary-card";
import { MetricCard } from "@/components/dashboard/metric-card";
import { RecurringExpensesCard } from "@/components/dashboard/recurring-expenses-card";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const [summary, cashflow, categories, recurring, cardSummary] = await Promise.all([
    api.summary(),
    api.cashflow(),
    api.categories(),
    api.recurring(),
    api.cardSummary()
  ]);

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Patrimônio bancário" value={summary.net_worth} icon={<Landmark size={18} />} />
        <MetricCard title="Saldo em contas" value={summary.accounts_balance} icon={<Wallet size={18} />} />
        <MetricCard title="Entradas do mês" value={summary.monthly_income} tone="success" icon={<TrendingUp size={18} />} />
        <MetricCard title="Gastos do mês" value={summary.monthly_expenses} tone="danger" icon={<TrendingDown size={18} />} />
        <MetricCard title="Resultado do mês" value={summary.monthly_result} tone={Number(summary.monthly_result) >= 0 ? "success" : "danger"} icon={<Banknote size={18} />} />
        <MetricCard title="Faturas abertas" value={summary.open_bills_total} tone="warning" icon={<CreditCard size={18} />} />
        <MetricCard title="Disponível estimado" value={summary.estimated_available} icon={<Wallet size={18} />} />
      </section>

      {summary.warnings.length ? (
        <Card className="border-warning/40">
          <CardContent className="flex items-center gap-3 py-1 text-sm text-warning">
            <AlertCircle size={18} />
            {summary.warnings.join(" ")}
          </CardContent>
        </Card>
      ) : null}

      <section className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Fluxo mensal</CardTitle>
          </CardHeader>
          <CardContent>
            <CashflowChart data={cashflow} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Gastos por categoria</CardTitle>
          </CardHeader>
          <CardContent>
            <CategoryPieChart data={categories} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Evolução de patrimônio</CardTitle>
          </CardHeader>
          <CardContent>
            <NetWorthChart data={cashflow} startingBalance={summary.accounts_balance} />
          </CardContent>
        </Card>
        <div className="grid gap-4">
          <RecurringExpensesCard items={recurring} />
          <CreditCardSummaryCard cards={cardSummary} />
        </div>
      </section>
    </div>
  );
}
