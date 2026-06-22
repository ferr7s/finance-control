"use client";

import { usePathname } from "next/navigation";
import { ShieldCheck } from "lucide-react";

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/transactions": "Transações",
  "/categories": "Categorias",
  "/cards": "Cartões",
  "/net-worth": "Patrimônio",
  "/insights": "Insights",
  "/agent": "Agente",
  "/settings/agent": "Agent / MCP"
};

export function Topbar() {
  const pathname = usePathname();
  const title = pageTitles[pathname] ?? "Finance Control";

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-border bg-background px-6 lg:px-8">
      <h1 className="text-base font-semibold tracking-wide text-white">{title}</h1>
      <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-white/30">
        <ShieldCheck size={12} />
        <span className="hidden sm:inline">Somente leitura</span>
      </div>
    </header>
  );
}
