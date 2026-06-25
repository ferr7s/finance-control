"use client";

import { useMemo, useState } from "react";
import { Check } from "lucide-react";

import { TransactionFilters } from "@/components/transactions/transaction-filters";
import { api } from "@/lib/api";
import { currency, shortDate } from "@/lib/formatters";
import type { Transaction, TransactionQueryFilters } from "@/types";

const categories = ["alimentação", "transporte", "saúde", "assinaturas", "moradia", "renda", "investimentos", "lazer", "educação", "vestuário", "beleza", "pets", "outros"];

function toApiFilters(filters: TransactionQueryFilters): TransactionQueryFilters {
  return {
    query: filters.query,
    start_date: filters.start_date ? `${filters.start_date}T00:00:00` : undefined,
    end_date: filters.end_date ? `${filters.end_date}T23:59:59` : undefined,
    category: filters.category,
    provider: filters.provider,
    type: filters.type
  };
}

function unique(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value)))).sort((a, b) => a.localeCompare(b));
}

function accountOrCardLabel(transaction: Transaction) {
  if (transaction.credit_card_id) return "Cartão";
  if (transaction.account_id) return "Conta";
  return transaction.payment_method || "-";
}

export function TransactionsTable({ initialTransactions }: { initialTransactions: Transaction[] }) {
  const [transactions, setTransactions] = useState(initialTransactions);
  const [filters, setFilters] = useState<TransactionQueryFilters>({});
  const [saved, setSaved] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const providerOptions = useMemo(() => unique(initialTransactions.map((tx) => tx.provider)), [initialTransactions]);
  const typeOptions = useMemo(() => unique(initialTransactions.map((tx) => tx.type)), [initialTransactions]);
  const categoryOptions = useMemo(() => unique([...categories, ...initialTransactions.map((tx) => tx.category)]), [initialTransactions]);

  async function applyFilters(nextFilters = filters) {
    setLoading(true);
    setError(null);
    try {
      const result = await api.transactions(toApiFilters(nextFilters));
      setTransactions(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha ao filtrar transações.");
    } finally {
      setLoading(false);
    }
  }

  async function resetFilters() {
    setFilters({});
    await applyFilters({});
  }

  async function updateCategory(transaction: Transaction, category: string) {
    try {
      const updated = await api.updateTransaction(transaction.id, { category });
      setTransactions((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setSaved(transaction.id);
      setTimeout(() => setSaved((current) => (current === transaction.id ? null : current)), 1500);
    } catch {
      // silently ignore — filters will reload fresh state on next apply
    }
  }

  return (
    <div className="space-y-4">
      <TransactionFilters
        filters={filters}
        categoryOptions={categoryOptions}
        providerOptions={providerOptions}
        typeOptions={typeOptions}
        loading={loading}
        onChange={setFilters}
        onApply={applyFilters}
        onReset={resetFilters}
      />
      {error ? <div className="border border-danger/40 bg-danger/10 p-3 text-sm text-danger">{error}</div> : null}
      <div className="overflow-x-auto border border-border">
        <table className="min-w-full divide-y divide-border text-sm">
          <thead className="bg-[#111923] text-left text-xs uppercase text-white/30">
            <tr>
              <th className="px-3 py-3">Data</th>
              <th className="px-3 py-3">Descrição</th>
              <th className="px-3 py-3">Valor</th>
              <th className="px-3 py-3">Categoria</th>
              <th className="px-3 py-3">Conta/cartão</th>
              <th className="px-3 py-3">Provedor</th>
              <th className="px-3 py-3">Tipo</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {transactions.map((tx) => (
              <tr key={tx.id} className="bg-muted/35">
                <td className="whitespace-nowrap px-3 py-3 text-white/40">{shortDate(tx.date)}</td>
                <td className="min-w-56 px-3 py-3">{tx.description}</td>
                <td className={`whitespace-nowrap px-3 py-3 font-medium ${Number(tx.amount) >= 0 ? "text-success" : "text-danger"}`}>
                  {currency(tx.amount)}
                </td>
                <td className="px-3 py-3">
                  <div className="flex items-center gap-1">
                    <select
                      className="h-8 border border-border bg-black px-2 text-xs"
                      defaultValue={tx.category || "outros"}
                      onChange={(event) => updateCategory(tx, event.target.value)}
                    >
                      {categories.map((category) => (
                        <option key={category} value={category}>
                          {category}
                        </option>
                      ))}
                    </select>
                    {saved === tx.id ? <Check size={12} className="text-success shrink-0" /> : null}
                  </div>
                </td>
                <td className="px-3 py-3 text-white/40">{accountOrCardLabel(tx)}</td>
                <td className="px-3 py-3 text-white/40">{tx.provider}</td>
                <td className="px-3 py-3 text-white/40">{tx.type}</td>
              </tr>
            ))}
            {transactions.length === 0 ? (
              <tr className="bg-muted/35">
                <td className="px-3 py-6 text-center text-white/30" colSpan={7}>
                  Nenhuma transação encontrada para os filtros aplicados.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
