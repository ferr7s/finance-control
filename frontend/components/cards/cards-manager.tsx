"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Pencil, Plus, Trash2, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api, type CreditCardBillPayload, type CreditCardPayload } from "@/lib/api";
import { currency, referenceMonth, shortDate } from "@/lib/formatters";
import type { CreditCard, CreditCardBill, CreditCardSummary, Transaction } from "@/types";

type BillsByCard = Record<string, CreditCardBill[]>;

const emptyCard: CreditCardPayload = {
  provider: "manual",
  name: "",
  brand: "",
  limit_total: null,
  limit_available: null,
  closing_day: null,
  due_day: null
};

const emptyBill: CreditCardBillPayload = {
  reference_month: `${new Date().toISOString().slice(0, 7)}-01`,
  due_date: null,
  closing_date: null,
  amount: "0.00",
  status: "open"
};

function optionalText(value: FormDataEntryValue | null) {
  const text = String(value ?? "").trim();
  return text ? text : null;
}

function optionalNumber(value: FormDataEntryValue | null) {
  const text = String(value ?? "").trim();
  return text ? Number(text) : null;
}

function optionalDecimal(value: FormDataEntryValue | null) {
  const text = String(value ?? "").trim();
  return text ? text : null;
}

function optionalDate(value: FormDataEntryValue | null) {
  const text = String(value ?? "").trim();
  return text ? text : null;
}

function cardPayload(formData: FormData): CreditCardPayload {
  return {
    provider: String(formData.get("provider") || "manual").trim(),
    name: String(formData.get("name") || "").trim(),
    brand: optionalText(formData.get("brand")),
    limit_total: optionalDecimal(formData.get("limit_total")),
    limit_available: optionalDecimal(formData.get("limit_available")),
    closing_day: optionalNumber(formData.get("closing_day")),
    due_day: optionalNumber(formData.get("due_day"))
  };
}

function billPayload(formData: FormData): CreditCardBillPayload {
  const referenceMonthValue = String(formData.get("reference_month") || new Date().toISOString().slice(0, 7));
  return {
    reference_month: `${referenceMonthValue}-01`,
    due_date: optionalDate(formData.get("due_date")),
    closing_date: optionalDate(formData.get("closing_date")),
    amount: String(formData.get("amount") || "0"),
    status: String(formData.get("status") || "open")
  };
}

function sortCards(cards: CreditCard[]) {
  return [...cards].sort((a, b) => a.name.localeCompare(b.name));
}

function sortBills(bills: CreditCardBill[]) {
  return [...bills].sort((a, b) => b.reference_month.localeCompare(a.reference_month));
}

function CardForm({
  card,
  busy,
  submitLabel,
  onSubmit,
  onCancel
}: {
  card?: CreditCard | CreditCardPayload;
  busy: boolean;
  submitLabel: string;
  onSubmit: (payload: CreditCardPayload) => Promise<void>;
  onCancel?: () => void;
}) {
  const defaults = card || emptyCard;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(cardPayload(new FormData(event.currentTarget)));
    if (!card) event.currentTarget.reset();
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-3 rounded-md border border-border bg-[#0f1620]/70 p-3 md:grid-cols-4">
      <label className="space-y-1 text-xs text-slate-400">
        Nome
        <Input name="name" required defaultValue={defaults.name} placeholder="Cartão principal" />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Provedor
        <Input name="provider" required defaultValue={defaults.provider} placeholder="manual" />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Bandeira
        <Input name="brand" defaultValue={defaults.brand || ""} placeholder="Visa" />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Limite total
        <Input name="limit_total" type="number" step="0.01" defaultValue={defaults.limit_total || ""} />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Limite disponível
        <Input name="limit_available" type="number" step="0.01" defaultValue={defaults.limit_available || ""} />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Fechamento
        <Input name="closing_day" type="number" min={1} max={31} defaultValue={defaults.closing_day || ""} />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Vencimento
        <Input name="due_day" type="number" min={1} max={31} defaultValue={defaults.due_day || ""} />
      </label>
      <div className="flex items-end gap-2">
        <Button disabled={busy} type="submit">
          {submitLabel}
        </Button>
        {onCancel ? (
          <Button className="bg-transparent text-slate-200 hover:bg-slate-800" disabled={busy} type="button" onClick={onCancel}>
            <X size={16} />
            Cancelar
          </Button>
        ) : null}
      </div>
    </form>
  );
}

function BillForm({
  bill,
  busy,
  submitLabel,
  onSubmit,
  onCancel
}: {
  bill?: CreditCardBill | CreditCardBillPayload;
  busy: boolean;
  submitLabel: string;
  onSubmit: (payload: CreditCardBillPayload) => Promise<void>;
  onCancel?: () => void;
}) {
  const defaults = bill || emptyBill;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(billPayload(new FormData(event.currentTarget)));
    if (!bill) event.currentTarget.reset();
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-3 rounded-md border border-border bg-[#0f1620]/70 p-3 md:grid-cols-5">
      <label className="space-y-1 text-xs text-slate-400">
        Referência
        <Input name="reference_month" required type="month" defaultValue={defaults.reference_month.slice(0, 7)} />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Vencimento
        <Input name="due_date" type="date" defaultValue={defaults.due_date || ""} />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Fechamento
        <Input name="closing_date" type="date" defaultValue={defaults.closing_date || ""} />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Valor
        <Input name="amount" required type="number" step="0.01" defaultValue={defaults.amount} />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Status
        <select
          name="status"
          defaultValue={defaults.status}
          className="h-9 w-full rounded-md border border-border bg-[#0f1620] px-3 text-sm text-slate-100 outline-none transition focus:border-accent"
        >
          <option value="open">Aberta</option>
          <option value="closed">Fechada</option>
          <option value="paid">Paga</option>
          <option value="unknown">Desconhecida</option>
        </select>
      </label>
      <div className="flex items-end gap-2 md:col-span-5">
        <Button disabled={busy} type="submit">
          {submitLabel}
        </Button>
        {onCancel ? (
          <Button className="bg-transparent text-slate-200 hover:bg-slate-800" disabled={busy} type="button" onClick={onCancel}>
            <X size={16} />
            Cancelar
          </Button>
        ) : null}
      </div>
    </form>
  );
}

export function CardsManager({
  initialCards,
  initialBillsByCard,
  summaries,
  transactions
}: {
  initialCards: CreditCard[];
  initialBillsByCard: BillsByCard;
  summaries: CreditCardSummary[];
  transactions: Transaction[];
}) {
  const router = useRouter();
  const [cards, setCards] = useState(() => sortCards(initialCards));
  const [billsByCard, setBillsByCard] = useState(() => initialBillsByCard);
  const [editingCardId, setEditingCardId] = useState<string | null>(null);
  const [addingBillFor, setAddingBillFor] = useState<string | null>(null);
  const [editingBillId, setEditingBillId] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const transactionsByCard = useMemo(() => {
    return transactions.reduce<Record<string, Transaction[]>>((groups, transaction) => {
      if (!transaction.credit_card_id) return groups;
      groups[transaction.credit_card_id] = [...(groups[transaction.credit_card_id] || []), transaction];
      return groups;
    }, {});
  }, [transactions]);

  async function run(action: string, task: () => Promise<void>) {
    setBusy(action);
    setError(null);
    try {
      await task();
      router.refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Não foi possível salvar os dados do cartão.");
    } finally {
      setBusy(null);
    }
  }

  async function createCard(payload: CreditCardPayload) {
    await run("create-card", async () => {
      const created = await api.createCreditCard(payload);
      setCards((current) => sortCards([...current, created]));
      setBillsByCard((current) => ({ ...current, [created.id]: [] }));
    });
  }

  async function updateCard(card: CreditCard, payload: CreditCardPayload) {
    await run(card.id, async () => {
      const updated = await api.updateCreditCard(card.id, payload);
      setCards((current) => sortCards(current.map((item) => (item.id === updated.id ? updated : item))));
      setEditingCardId(null);
    });
  }

  async function deleteCard(card: CreditCard) {
    if (!window.confirm(`Excluir o cartão ${card.name} e suas faturas?`)) return;
    await run(card.id, async () => {
      await api.deleteCreditCard(card.id);
      setCards((current) => current.filter((item) => item.id !== card.id));
      setBillsByCard((current) => {
        const next = { ...current };
        delete next[card.id];
        return next;
      });
    });
  }

  async function createBill(cardId: string, payload: CreditCardBillPayload) {
    await run(`create-bill-${cardId}`, async () => {
      const created = await api.createBill(cardId, payload);
      setBillsByCard((current) => ({ ...current, [cardId]: sortBills([...(current[cardId] || []), created]) }));
      setAddingBillFor(null);
    });
  }

  async function updateBill(bill: CreditCardBill, payload: CreditCardBillPayload) {
    await run(bill.id, async () => {
      const updated = await api.updateBill(bill.id, payload);
      setBillsByCard((current) => ({
        ...current,
        [updated.credit_card_id]: sortBills((current[updated.credit_card_id] || []).map((item) => (item.id === updated.id ? updated : item)))
      }));
      setEditingBillId(null);
    });
  }

  async function deleteBill(bill: CreditCardBill) {
    if (!window.confirm(`Excluir a fatura de ${referenceMonth(bill.reference_month)}?`)) return;
    await run(bill.id, async () => {
      await api.deleteBill(bill.id);
      setBillsByCard((current) => ({
        ...current,
        [bill.credit_card_id]: (current[bill.credit_card_id] || []).filter((item) => item.id !== bill.id)
      }));
    });
  }

  return (
    <div className="space-y-4">
      {error ? <div className="rounded-md border border-danger/40 bg-danger/10 p-3 text-sm text-danger">{error}</div> : null}
      <Card>
        <CardHeader>
          <CardTitle>Novo cartão</CardTitle>
        </CardHeader>
        <CardContent>
          <CardForm busy={busy === "create-card"} submitLabel="Adicionar cartão" onSubmit={createCard} />
        </CardContent>
      </Card>

      <div className="grid gap-4 xl:grid-cols-2">
        {cards.map((card) => {
          const summary = summaries.find((item) => item.id === card.id);
          const bills = billsByCard[card.id] || [];
          const cardTransactions = (transactionsByCard[card.id] || []).slice(0, 5);
          return (
            <Card key={card.id}>
              <CardHeader>
                <div>
                  <CardTitle>{card.name}</CardTitle>
                  <div className="mt-1 text-xs text-slate-500">{card.provider}{card.brand ? ` · ${card.brand}` : ""}</div>
                </div>
                <div className="flex gap-2">
                  <Button className="size-8 bg-transparent px-0 text-slate-200 hover:bg-slate-800" title="Editar cartão" onClick={() => setEditingCardId(card.id)}>
                    <Pencil size={15} />
                  </Button>
                  <Button className="size-8 bg-transparent px-0 text-danger hover:bg-danger/10" disabled={busy === card.id} title="Excluir cartão" onClick={() => deleteCard(card)}>
                    <Trash2 size={15} />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {editingCardId === card.id ? (
                  <CardForm
                    card={card}
                    busy={busy === card.id}
                    submitLabel="Salvar cartão"
                    onSubmit={(payload) => updateCard(card, payload)}
                    onCancel={() => setEditingCardId(null)}
                  />
                ) : null}

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
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-xs font-medium uppercase text-slate-500">Faturas</div>
                    <Button className="h-8 bg-transparent text-slate-200 hover:bg-slate-800" onClick={() => setAddingBillFor(card.id)}>
                      <Plus size={15} />
                      Fatura
                    </Button>
                  </div>
                  {addingBillFor === card.id ? (
                    <BillForm
                      busy={busy === `create-bill-${card.id}`}
                      submitLabel="Adicionar fatura"
                      onSubmit={(payload) => createBill(card.id, payload)}
                      onCancel={() => setAddingBillFor(null)}
                    />
                  ) : null}
                  {bills.slice(0, 4).map((bill) => (
                    <div key={bill.id} className="rounded-md border border-border p-3 text-sm">
                      {editingBillId === bill.id ? (
                        <BillForm
                          bill={bill}
                          busy={busy === bill.id}
                          submitLabel="Salvar fatura"
                          onSubmit={(payload) => updateBill(bill, payload)}
                          onCancel={() => setEditingBillId(null)}
                        />
                      ) : (
                        <div className="grid grid-cols-[1fr_auto] gap-3">
                          <div>
                            <div className="font-medium">{referenceMonth(bill.reference_month)}</div>
                            <div className="text-xs text-slate-500">
                              Venc. {bill.due_date ? shortDate(bill.due_date) : "-"} · Fech. {bill.closing_date ? shortDate(bill.closing_date) : "-"}
                            </div>
                          </div>
                          <div className="flex items-start gap-3 text-right">
                            <div>
                              <div className="font-semibold">{currency(bill.amount)}</div>
                              <Badge>{bill.status}</Badge>
                            </div>
                            <div className="flex gap-2">
                              <Button className="size-8 bg-transparent px-0 text-slate-200 hover:bg-slate-800" title="Editar fatura" onClick={() => setEditingBillId(bill.id)}>
                                <Pencil size={15} />
                              </Button>
                              <Button className="size-8 bg-transparent px-0 text-danger hover:bg-danger/10" disabled={busy === bill.id} title="Excluir fatura" onClick={() => deleteBill(bill)}>
                                <Trash2 size={15} />
                              </Button>
                            </div>
                          </div>
                        </div>
                      )}
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
                  {cardTransactions.length === 0 ? <div className="rounded-md border border-border p-3 text-sm text-slate-500">Sem transações associadas a este cartão.</div> : null}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
      {cards.length === 0 ? <div className="rounded-md border border-border p-4 text-sm text-slate-500">Nenhum cartão cadastrado.</div> : null}
    </div>
  );
}
