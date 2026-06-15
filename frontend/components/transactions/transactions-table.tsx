"use client";

import { useMemo, useState } from "react";
import { Save } from "lucide-react";

import { Button } from "@/components/ui/button";
import { TransactionFilters } from "@/components/transactions/transaction-filters";
import { api } from "@/lib/api";
import { currency, shortDate } from "@/lib/formatters";
import type { Transaction } from "@/types";

const categories = ["alimentação", "transporte", "saúde", "assinaturas", "moradia", "renda", "investimentos", "lazer", "outros"];

export function TransactionsTable({ initialTransactions }: { initialTransactions: Transaction[] }) {
  const [transactions, setTransactions] = useState(initialTransactions);
  const [search, setSearch] = useState("");
  const [saving, setSaving] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return transactions;
    return transactions.filter((tx) =>
      [tx.description, tx.provider, tx.type, tx.category, tx.payment_method].some((value) => (value || "").toLowerCase().includes(q))
    );
  }, [transactions, search]);

  async function updateCategory(transaction: Transaction, category: string) {
    setSaving(transaction.id);
    try {
      const updated = await api.updateTransaction(transaction.id, { category });
      setTransactions((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    } finally {
      setSaving(null);
    }
  }

  return (
    <div className="space-y-4">
      <TransactionFilters onSearch={setSearch} />
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="min-w-full divide-y divide-border text-sm">
          <thead className="bg-[#111923] text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="px-3 py-3">Data</th>
              <th className="px-3 py-3">Descrição</th>
              <th className="px-3 py-3">Valor</th>
              <th className="px-3 py-3">Categoria</th>
              <th className="px-3 py-3">Provedor</th>
              <th className="px-3 py-3">Tipo</th>
              <th className="px-3 py-3">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {filtered.map((tx) => (
              <tr key={tx.id} className="bg-muted/35">
                <td className="whitespace-nowrap px-3 py-3 text-slate-400">{shortDate(tx.date)}</td>
                <td className="min-w-56 px-3 py-3">{tx.description}</td>
                <td className={`whitespace-nowrap px-3 py-3 font-medium ${Number(tx.amount) >= 0 ? "text-success" : "text-danger"}`}>
                  {currency(tx.amount)}
                </td>
                <td className="px-3 py-3">
                  <select
                    className="h-8 rounded-md border border-border bg-[#0f1620] px-2 text-xs"
                    defaultValue={tx.category || "outros"}
                    onChange={(event) => updateCategory(tx, event.target.value)}
                  >
                    {categories.map((category) => (
                      <option key={category} value={category}>
                        {category}
                      </option>
                    ))}
                  </select>
                </td>
                <td className="px-3 py-3 text-slate-400">{tx.provider}</td>
                <td className="px-3 py-3 text-slate-400">{tx.type}</td>
                <td className="px-3 py-3">
                  <Button className="size-8 px-0" disabled={saving === tx.id} title="Categoria salva ao alterar">
                    <Save size={14} />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
