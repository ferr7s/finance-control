import { CardsManager } from "@/components/cards/cards-manager";
import { api } from "@/lib/api";
import type { CreditCardBill } from "@/types";

export const dynamic = "force-dynamic";

export default async function CardsPage() {
  const [cards, summaries, transactions] = await Promise.all([api.creditCards(), api.cardSummary(), api.transactions()]);
  const billGroups = await Promise.all(cards.map(async (card) => ({ cardId: card.id, bills: await api.bills(card.id) })));
  const billsByCard = billGroups.reduce<Record<string, CreditCardBill[]>>((groups, group) => {
    groups[group.cardId] = group.bills;
    return groups;
  }, {});

  return <CardsManager initialCards={cards} initialBillsByCard={billsByCard} summaries={summaries} transactions={transactions} />;
}
