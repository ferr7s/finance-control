import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TransactionsTable } from "@/components/transactions/transactions-table";
import { UploadCsvCard } from "@/components/transactions/upload-csv-card";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function TransactionsPage() {
  const transactions = await api.transactions();
  return (
    <div className="space-y-6">
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
