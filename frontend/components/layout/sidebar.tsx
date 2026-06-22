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
    <aside className="fixed inset-y-0 left-0 hidden w-56 border-r border-border bg-background lg:flex lg:flex-col">
      <Link href="/dashboard" className="flex items-center gap-3 border-b border-border px-5 py-5">
        <div className="flex size-7 shrink-0 items-center justify-center border border-white">
          <BarChart3 size={14} className="text-white" />
        </div>
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-white">Finance</div>
          <div className="text-[10px] tracking-widest text-white/30">CONTROL</div>
        </div>
      </Link>

      <nav className="flex-1 px-3 py-4">
        {items.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex h-9 items-center gap-3 px-2 text-xs tracking-wide text-white/40 transition hover:text-white",
                active && "text-white"
              )}
            >
              <Icon size={14} className={cn("shrink-0", active ? "text-white" : "text-white/30")} />
              <span>{item.label}</span>
              {active && <span className="ml-auto h-1 w-1 rounded-full bg-white" />}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border px-3 py-4 text-[10px] uppercase tracking-widest text-white/20">
        <div className="px-2 py-1">Local-first</div>
      </div>
    </aside>
  );
}
