import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { currency } from "@/lib/formatters";
import type { RecurringExpense } from "@/types";

export function RecurringExpensesCard({ items }: { items: RecurringExpense[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Gastos recorrentes</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.slice(0, 5).map((item) => (
          <div key={`${item.description}-${item.category}`} className="flex items-center justify-between gap-3 text-sm">
            <div>
              <div className="text-slate-100">{item.description}</div>
              <div className="text-xs text-slate-500">{item.occurrences} ocorrências</div>
            </div>
            <div className="font-medium">{currency(item.amount)}</div>
          </div>
        ))}
        {items.length === 0 ? <div className="text-sm text-slate-500">Sem recorrências detectadas.</div> : null}
      </CardContent>
    </Card>
  );
}
