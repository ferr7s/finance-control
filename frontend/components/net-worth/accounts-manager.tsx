"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Pencil, Trash2, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, type AccountPayload } from "@/lib/api";
import { currency } from "@/lib/formatters";
import type { Account } from "@/types";

const emptyAccount: AccountPayload = {
  provider: "manual",
  name: "",
  type: "checking",
  currency: "BRL",
  current_balance: "0.00",
  institution_name: "",
  branch: "",
  account_number_masked: ""
};

function valueOrNull(value: FormDataEntryValue | null) {
  const text = String(value ?? "").trim();
  return text ? text : null;
}

function accountPayload(formData: FormData): AccountPayload {
  return {
    provider: String(formData.get("provider") || "manual").trim(),
    name: String(formData.get("name") || "").trim(),
    type: String(formData.get("type") || "checking"),
    currency: String(formData.get("currency") || "BRL").trim().toUpperCase(),
    current_balance: String(formData.get("current_balance") || "0"),
    institution_name: valueOrNull(formData.get("institution_name")),
    branch: valueOrNull(formData.get("branch")),
    account_number_masked: valueOrNull(formData.get("account_number_masked"))
  };
}

function sortAccounts(accounts: Account[]) {
  return [...accounts].sort((a, b) => a.name.localeCompare(b.name));
}

function AccountForm({
  account,
  busy,
  submitLabel,
  onSubmit,
  onCancel
}: {
  account?: Account | AccountPayload;
  busy: boolean;
  submitLabel: string;
  onSubmit: (payload: AccountPayload) => Promise<void>;
  onCancel?: () => void;
}) {
  const defaults = account || emptyAccount;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(accountPayload(new FormData(event.currentTarget)));
    if (!account) {
      event.currentTarget.reset();
    }
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-3 rounded-md border border-border bg-[#0f1620]/70 p-3 md:grid-cols-4">
      <label className="space-y-1 text-xs text-slate-400">
        Nome
        <Input name="name" required defaultValue={defaults.name} placeholder="Conta corrente" />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Provedor
        <Input name="provider" required defaultValue={defaults.provider} placeholder="manual" />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Tipo
        <select
          name="type"
          defaultValue={defaults.type}
          className="h-9 w-full rounded-md border border-border bg-[#0f1620] px-3 text-sm text-slate-100 outline-none transition focus:border-accent"
        >
          <option value="checking">Corrente</option>
          <option value="savings">Poupança</option>
          <option value="investment">Investimento</option>
          <option value="cash">Dinheiro</option>
          <option value="other">Outro</option>
        </select>
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Saldo atual
        <Input name="current_balance" required type="number" step="0.01" defaultValue={defaults.current_balance} />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Moeda
        <Input name="currency" required maxLength={3} defaultValue={defaults.currency} />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Instituição
        <Input name="institution_name" defaultValue={defaults.institution_name || ""} placeholder="Banco" />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Agência
        <Input name="branch" defaultValue={defaults.branch || ""} />
      </label>
      <label className="space-y-1 text-xs text-slate-400">
        Número mascarado
        <Input name="account_number_masked" defaultValue={defaults.account_number_masked || ""} placeholder="****1234" />
      </label>
      <div className="flex items-end gap-2 md:col-span-4">
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

export function AccountsManager({ initialAccounts }: { initialAccounts: Account[] }) {
  const router = useRouter();
  const [accounts, setAccounts] = useState(() => sortAccounts(initialAccounts));
  const [editingId, setEditingId] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const total = useMemo(() => accounts.reduce((sum, account) => sum + Number(account.current_balance || 0), 0), [accounts]);

  async function run(action: string, task: () => Promise<void>) {
    setBusy(action);
    setError(null);
    try {
      await task();
      router.refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Não foi possível salvar a conta.");
    } finally {
      setBusy(null);
    }
  }

  async function createAccount(payload: AccountPayload) {
    await run("create", async () => {
      const created = await api.createAccount(payload);
      setAccounts((current) => sortAccounts([...current, created]));
    });
  }

  async function updateAccount(account: Account, payload: AccountPayload) {
    await run(account.id, async () => {
      const updated = await api.updateAccount(account.id, payload);
      setAccounts((current) => sortAccounts(current.map((item) => (item.id === updated.id ? updated : item))));
      setEditingId(null);
    });
  }

  async function deleteAccount(account: Account) {
    if (!window.confirm(`Excluir a conta ${account.name}?`)) return;
    await run(account.id, async () => {
      await api.deleteAccount(account.id);
      setAccounts((current) => current.filter((item) => item.id !== account.id));
    });
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="text-sm font-medium text-slate-200">Contas bancárias</div>
          <div className="text-xs text-slate-500">Saldo cadastrado: {currency(total)}</div>
        </div>
      </div>
      {error ? <div className="rounded-md border border-danger/40 bg-danger/10 p-3 text-sm text-danger">{error}</div> : null}
      <AccountForm busy={busy === "create"} submitLabel="Adicionar conta" onSubmit={createAccount} />
      <div className="space-y-3">
        {accounts.map((account) => (
          <div key={account.id} className="rounded-md border border-border p-3 text-sm">
            {editingId === account.id ? (
              <AccountForm
                account={account}
                busy={busy === account.id}
                submitLabel="Salvar conta"
                onSubmit={(payload) => updateAccount(account, payload)}
                onCancel={() => setEditingId(null)}
              />
            ) : (
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="font-medium">{account.name}</div>
                  <div className="text-xs text-slate-500">
                    {account.institution_name || account.provider} · {account.type} · {account.currency}
                  </div>
                </div>
                <div className="flex items-center justify-between gap-3 sm:justify-end">
                  <div className="font-semibold">{currency(account.current_balance)}</div>
                  <div className="flex gap-2">
                    <Button className="size-8 bg-transparent px-0 text-slate-200 hover:bg-slate-800" title="Editar conta" onClick={() => setEditingId(account.id)}>
                      <Pencil size={15} />
                    </Button>
                    <Button
                      className="size-8 bg-transparent px-0 text-danger hover:bg-danger/10"
                      disabled={busy === account.id}
                      title="Excluir conta"
                      onClick={() => deleteAccount(account)}
                    >
                      <Trash2 size={15} />
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
        {accounts.length === 0 ? <div className="rounded-md border border-border p-3 text-sm text-slate-500">Nenhuma conta cadastrada.</div> : null}
      </div>
    </div>
  );
}
