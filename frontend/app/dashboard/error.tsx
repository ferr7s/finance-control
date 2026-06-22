"use client";

import { AlertTriangle, RefreshCw, ServerCrash } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function DashboardError({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const details = error.message && error.message !== "An error occurred in the Server Components render but no message was provided"
    ? error.message
    : "O dashboard depende da API local em http://localhost:8000. Se a API ou o banco local não estiverem ativos, a página não consegue carregar os dados.";

  return (
    <div className="space-y-4">
      <Card className="border-danger/40">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center bg-danger/10 text-danger">
              <ServerCrash size={18} />
            </div>
            <div>
              <CardTitle>Não foi possível carregar o dashboard</CardTitle>
              <div className="mt-1 text-sm text-white/40">
                A interface abriu, mas a camada de dados local não respondeu.
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div className="border border-border bg-black p-3 text-white/60">{details}</div>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="border border-border p-3">
              <div className="mb-1 flex items-center gap-2 font-medium text-white/80">
                <AlertTriangle size={15} />
                Verificações locais
              </div>
              <div className="text-white/40">API esperada em `http://localhost:8000`</div>
              <div className="text-white/40">PostgreSQL esperado em `localhost:5432`</div>
            </div>
            <div className="border border-border p-3">
              <div className="mb-1 font-medium text-white/80">Ação recomendada</div>
              <div className="text-white/40">Suba backend e banco, depois tente recarregar esta rota.</div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={reset}>
              <RefreshCw size={15} />
              Tentar novamente
            </Button>
            <Button className="bg-transparent text-white/80 hover:bg-white/10" onClick={() => window.location.assign("/cards")}>
              Ir para cartões
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
