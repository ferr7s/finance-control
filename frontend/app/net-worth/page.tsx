import { AlertCircle } from "lucide-react";

import { NetWorthChart } from "@/components/charts/net-worth-chart";
import { AccountsManager } from "@/components/net-worth/accounts-manager";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { currency } from "@/lib/formatters";

export const dynamic = "force-dynamic";

export default async function NetWorthPage() {
  const [netWorth, accounts, cashflow] = await Promise.all([api.netWorth(), api.accounts(), api.cashflow()]);

  return (
    <div className="space-y-4">
      <section className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Patrimônio bancário total</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold">{currency(netWorth.net_worth)}</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Saldo em contas</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold">{currency(netWorth.accounts_balance)}</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Faturas em aberto</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-warning">{currency(netWorth.open_bills_total)}</CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Evolução histórica</CardTitle>
        </CardHeader>
        <CardContent>
          <NetWorthChart data={cashflow} startingBalance={netWorth.accounts_balance} />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <AccountsManager initialAccounts={accounts} />
        </CardContent>
      </Card>

      <Card className="border-warning/40">
        <CardContent className="flex items-center gap-3 py-1 text-sm text-warning">
          <AlertCircle size={18} />
          Evolução histórica é estimada com base nos dados transacionais disponíveis.
        </CardContent>
      </Card>
    </div>
  );
}
