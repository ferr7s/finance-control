import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { currency, referenceMonth, shortDate } from "@/lib/formatters";

export const dynamic = "force-dynamic";

export default async function CardsPage() {
  const [cards, summaries, transactions] = await Promise.all([api.creditCards(), api.cardSummary(), api.transactions()]);
  const billsByCard = await Promise.all(cards.map(async (card) => ({ cardId: card.id, bills: await api.bills(card.id) })));

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {cards.map((card) => {
        const summary = summaries.find((item) => item.id === card.id);
        const bills = billsByCard.find((item) => item.cardId === card.id)?.bills || [];
        const cardTransactions = transactions.filter((transaction) => transaction.credit_card_id === card.id).slice(0, 5);
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
              <div className="space-y-2">
                <div className="text-xs font-medium uppercase text-slate-500">Faturas</div>
                {bills.slice(0, 4).map((bill) => (
                  <div key={bill.id} className="grid grid-cols-[1fr_auto] gap-3 rounded-md border border-border p-3 text-sm">
                    <div>
                      <div className="font-medium">{referenceMonth(bill.reference_month)}</div>
                      <div className="text-xs text-slate-500">
                        Venc. {bill.due_date ? shortDate(bill.due_date) : "-"} · Fech. {bill.closing_date ? shortDate(bill.closing_date) : "-"}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">{currency(bill.amount)}</div>
                      <div className="text-xs text-slate-500">{bill.status}</div>
                    </div>
                  </div>
                ))}
                {bills.length === 0 ? <div className="rounded-md border border-border p-3 text-sm text-slate-500">Sem faturas cadastradas.</div> : null}
              </div>
              <div className="space-y-2">
                <div className="text-xs font-medium uppercase text-slate-500">Transações associadas</div>
                {cardTransactions.map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between gap-3 rounded-md border border-border p-3 text-sm">
                    <div>
                      <div className="font-medium">{transaction.description}</div>
                      <div className="text-xs text-slate-500">{shortDate(transaction.date)}</div>
                    </div>
                    <div className="font-semibold text-danger">{currency(transaction.amount)}</div>
                  </div>
                ))}
                {cardTransactions.length === 0 ? (
                  <div className="rounded-md border border-border p-3 text-sm text-slate-500">Sem transações associadas a este cartão.</div>
                ) : null}
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
