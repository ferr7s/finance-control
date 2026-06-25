import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TransactionsTable } from "@/components/transactions/transactions-table";
import { SyncButton } from "@/components/transactions/sync-button";
import { UploadCsvCard } from "@/components/transactions/upload-csv-card";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function TransactionsPage() {
  const transactions = await api.transactions();
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <span className="text-[10px] uppercase tracking-widest text-white/30">Bancos conectados: Flash · Itaú · Nubank</span>
        <SyncButton />
      </div>
      <UploadCsvCard />
      <Card>
        <CardHeader>
          <CardTitle>Transações</CardTitle>
        </CardHeader>
        <CardContent>
          <TransactionsTable initialTransactions={transactions} />
        </CardContent>
      </Card>
    </div>
  );
}
