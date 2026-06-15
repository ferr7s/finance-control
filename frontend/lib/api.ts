import type {
  Account,
  AgentAnalysis,
  AgentTool,
  CategoryBreakdownItem,
  CreditCard,
  CreditCardBill,
  CreditCardSummary,
  DashboardSummary,
  Insight,
  MonthlyCashflowPoint,
  RecurringExpense,
  Transaction
} from "@/types";

function baseUrl() {
  if (typeof window === "undefined") {
    return process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl()}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(init?.headers || {})
    }
  });
  if (!response.ok) {
    throw new Error(`API ${path} failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  summary: () => apiFetch<DashboardSummary>("/api/dashboard/summary"),
  cashflow: () => apiFetch<MonthlyCashflowPoint[]>("/api/dashboard/monthly-cashflow"),
  categories: () => apiFetch<CategoryBreakdownItem[]>("/api/dashboard/category-breakdown"),
  netWorth: () => apiFetch<{ accounts_balance: string; open_bills_total: string; net_worth: string }>("/api/dashboard/net-worth"),
  recurring: () => apiFetch<RecurringExpense[]>("/api/dashboard/recurring-expenses"),
  cardSummary: () => apiFetch<CreditCardSummary[]>("/api/dashboard/credit-card-summary"),
  transactions: () => apiFetch<Transaction[]>("/api/transactions"),
  updateTransaction: (id: string, payload: Partial<Transaction>) =>
    apiFetch<Transaction>(`/api/transactions/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  accounts: () => apiFetch<Account[]>("/api/accounts"),
  creditCards: () => apiFetch<CreditCard[]>("/api/credit-cards"),
  bills: (cardId: string) => apiFetch<CreditCardBill[]>(`/api/credit-cards/${cardId}/bills`),
  insights: () => apiFetch<Insight[]>("/api/insights"),
  generateInsights: () => apiFetch<Insight[]>("/api/insights/generate", { method: "POST", body: "{}" }),
  analyses: () => apiFetch<AgentAnalysis[]>("/api/agent-analyses"),
  importCsv: (formData: FormData) => apiFetch<{ total_rows: number; imported: number; ignored: number; errors: string[] }>("/api/import/bank-csv", { method: "POST", body: formData }),
  manifest: () => apiFetch<{ tools: AgentTool[] }>("/agent_tools_manifest.json")
};

export function asNumber(value: string | number | null | undefined) {
  return Number(value ?? 0);
}
