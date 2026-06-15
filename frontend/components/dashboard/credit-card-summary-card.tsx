import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { currency } from "@/lib/formatters";
import type { CreditCardSummary } from "@/types";

export function CreditCardSummaryCard({ cards }: { cards: CreditCardSummary[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Cartões e faturas</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {cards.map((card) => (
          <div key={card.id} className="rounded-md border border-border p-3">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-sm font-medium">{card.name}</div>
                <div className="text-xs text-slate-500">{card.provider}</div>
              </div>
              <div className="text-right text-sm font-semibold">{currency(card.open_bill_amount)}</div>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-400">
              <span>Fecha dia {card.closing_day ?? "-"}</span>
              <span>Vence dia {card.due_day ?? "-"}</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
