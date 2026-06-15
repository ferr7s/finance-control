import { ShieldCheck } from "lucide-react";

import { Badge } from "@/components/ui/badge";

export function Topbar() {
  return (
    <header className="sticky top-0 z-20 border-b border-border bg-background/90 px-4 py-3 backdrop-blur lg:px-8">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold">Finance Control</h1>
          <p className="text-xs text-slate-500">Dashboard bancário, importação CSV e ferramentas read-only para agentes.</p>
        </div>
        <Badge className="hidden gap-2 border-accent/30 text-accent sm:inline-flex">
          <ShieldCheck size={14} />
          Somente leitura para agentes
        </Badge>
      </div>
    </header>
  );
}
