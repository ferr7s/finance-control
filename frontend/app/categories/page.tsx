import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CategoryPieChart } from "@/components/charts/category-pie-chart";
import { api } from "@/lib/api";
import { currency, percent } from "@/lib/formatters";

export const dynamic = "force-dynamic";

export default async function CategoriesPage() {
  const categories = await api.categories();
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
                <div className="text-xs text-slate-500">Mês atual vs mês anterior disponível com mais histórico importado</div>
              </div>
              <div className="text-right">
                <div className="text-sm font-semibold">{currency(item.amount)}</div>
                <div className="text-xs text-slate-500">{percent(item.percentage)}</div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
