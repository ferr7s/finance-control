import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { currency } from "@/lib/formatters";

export const dynamic = "force-dynamic";

export default async function CardsPage() {
  const [cards, summaries] = await Promise.all([api.creditCards(), api.cardSummary()]);
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {cards.map((card) => {
        const summary = summaries.find((item) => item.id === card.id);
        return (
          <Card key={card.id}>
            <CardHeader>
              <CardTitle>{card.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="text-slate-500">Limite total</div>
                  <div className="font-semibold">{currency(card.limit_total)}</div>
                </div>
                <div>
                  <div className="text-slate-500">Limite disponível</div>
                  <div className="font-semibold">{currency(card.limit_available)}</div>
                </div>
                <div>
                  <div className="text-slate-500">Fatura atual</div>
                  <div className="font-semibold text-warning">{currency(summary?.open_bill_amount)}</div>
                </div>
                <div>
                  <div className="text-slate-500">Fechamento / vencimento</div>
                  <div className="font-semibold">
                    {card.closing_day ?? "-"} / {card.due_day ?? "-"}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
