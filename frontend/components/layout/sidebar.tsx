"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Bot, CreditCard, Gauge, Landmark, Lightbulb, ListFilter, Settings, Tags } from "lucide-react";

import { cn } from "@/lib/utils";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/transactions", label: "Transações", icon: ListFilter },
  { href: "/categories", label: "Categorias", icon: Tags },
  { href: "/cards", label: "Cartões", icon: CreditCard },
  { href: "/net-worth", label: "Patrimônio", icon: Landmark },
  { href: "/insights", label: "Insights", icon: Lightbulb },
  { href: "/agent", label: "Agente", icon: Bot },
  { href: "/settings/agent", label: "Agent / MCP", icon: Settings }
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-border bg-[#0d131b] p-4 lg:block">
      <Link href="/dashboard" className="mb-8 flex items-center gap-3">
        <div className="flex size-9 items-center justify-center rounded-md bg-accent text-slate-950">
          <BarChart3 size={20} />
        </div>
        <div>
          <div className="text-sm font-semibold">Finance Control</div>
          <div className="text-xs text-slate-500">Local-first</div>
        </div>
      </Link>
      <nav className="space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex h-10 items-center gap-3 rounded-md px-3 text-sm text-slate-400 transition hover:bg-slate-800 hover:text-slate-100",
                active && "bg-slate-800 text-slate-50"
              )}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
