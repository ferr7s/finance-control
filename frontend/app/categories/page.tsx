import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CategoryPieChart } from "@/components/charts/category-pie-chart";
import { api } from "@/lib/api";
import { currency, percent, shortDate } from "@/lib/formatters";

export const dynamic = "force-dynamic";

export default async function CategoriesPage() {
  const [categories, largestExpenses] = await Promise.all([api.categories(), api.largestExpenses()]);
  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_1.2fr]">
      <Card>
        <CardHeader>
          <CardTitle>Distribuição por categoria</CardTitle>
        </CardHeader>
        <CardContent>
          <CategoryPieChart data={categories} />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Ranking de categorias</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {categories.map((item) => (
            <div key={item.category} className="flex items-center justify-between gap-3 rounded-md border border-border p-3">
              <div>
                <div className="text-sm font-medium">{item.category}</div>
                <div className="text-xs text-slate-500">Participação nos gastos do mês atual</div>
              </div>
              <div className="text-right">
                <div className="text-sm font-semibold">{currency(item.amount)}</div>
                <div className="text-xs text-slate-500">{percent(item.percentage)}</div>
              </div>
            </div>
          ))}
          {categories.length === 0 ? <div className="text-sm text-slate-500">Sem gastos categorizados no mês atual.</div> : null}
        </CardContent>
      </Card>
      <Card className="xl:col-span-2">
        <CardHeader>
          <CardTitle>Top descrições e estabelecimentos</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {largestExpenses.map((expense) => (
            <div key={`${expense.date}-${expense.description}-${expense.amount}`} className="rounded-md border border-border p-3 text-sm">
              <div className="font-medium">{expense.description}</div>
              <div className="mt-1 text-xs text-slate-500">
                {expense.category || "outros"} · {expense.provider} · {shortDate(expense.date)}
              </div>
              <div className="mt-3 font-semibold text-danger">{currency(expense.amount)}</div>
            </div>
          ))}
          {largestExpenses.length === 0 ? <div className="text-sm text-slate-500">Sem transações suficientes para ranking.</div> : null}
        </CardContent>
      </Card>
    </div>
  );
}
