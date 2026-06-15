export type DecimalString = string;

export type Account = {
  id: string;
  provider: string;
  name: string;
  type: string;
  currency: string;
  current_balance: DecimalString;
  institution_name?: string | null;
  branch?: string | null;
  account_number_masked?: string | null;
};

export type CreditCard = {
  id: string;
  provider: string;
  name: string;
  brand?: string | null;
  limit_total?: DecimalString | null;
  limit_available?: DecimalString | null;
  closing_day?: number | null;
  due_day?: number | null;
};

export type CreditCardBill = {
  id: string;
  credit_card_id: string;
  reference_month: string;
  due_date?: string | null;
  closing_date?: string | null;
  amount: DecimalString;
  status: string;
};

export type Transaction = {
  id: string;
  external_id?: string | null;
  provider: string;
  account_id?: string | null;
  credit_card_id?: string | null;
  bill_id?: string | null;
  date: string;
  description: string;
  amount: DecimalString;
  type: string;
  payment_method?: string | null;
  category?: string | null;
  subcategory?: string | null;
  merchant?: string | null;
  is_recurring: boolean;
};

export type Insight = {
  id: string;
  type: string;
  title: string;
  content: string;
  severity: "info" | "warning" | "danger" | "success" | string;
  source: string;
  created_at: string;
};

export type AgentAnalysis = {
  id: string;
  source: string;
  title: string;
  content: string;
  metadata?: Record<string, unknown> | null;
  metadata_json?: Record<string, unknown> | null;
  created_at: string;
};

export type DashboardSummary = {
  net_worth: DecimalString;
  accounts_balance: DecimalString;
  monthly_income: DecimalString;
  monthly_expenses: DecimalString;
  monthly_result: DecimalString;
  open_bills_total: DecimalString;
  estimated_available?: DecimalString | null;
  warnings: string[];
};

export type MonthlyCashflowPoint = {
  month: string;
  income: DecimalString;
  expenses: DecimalString;
  result: DecimalString;
};

export type CategoryBreakdownItem = {
  category: string;
  amount: DecimalString;
  percentage: number;
};

export type RecurringExpense = {
  description: string;
  category?: string | null;
  amount: DecimalString;
  occurrences: number;
};

export type CreditCardSummary = {
  id: string;
  name: string;
  provider: string;
  limit_total?: DecimalString | null;
  limit_available?: DecimalString | null;
  open_bill_amount: DecimalString;
  due_day?: number | null;
  closing_day?: number | null;
};

export type AgentTool = {
  name: string;
  description: string;
  endpoint: string;
  method: string;
  readonly: boolean;
  write_safe: boolean;
  safety_note: string;
};
