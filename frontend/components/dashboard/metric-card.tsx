import { ReactNode } from "react";

import { Card } from "@/components/ui/card";
import { currency } from "@/lib/formatters";

export function MetricCard({
  title,
  value,
  icon,
  tone = "default"
}: {
  title: string;
  value: string | number | null | undefined;
  icon?: ReactNode;
  tone?: "default" | "success" | "danger" | "warning";
}) {
  const toneClass = {
    default: "text-white",
    success: "text-white",
    danger: "text-white/60",
    warning: "text-white/80"
  }[tone];

  return (
    <Card className="min-h-28">
      <div className="flex items-center justify-between gap-3 text-[10px] uppercase tracking-widest text-white/30">
        <span>{title}</span>
        <span className="text-white/20">{icon}</span>
      </div>
      <div className={`mt-4 font-mono text-2xl font-semibold tracking-tight ${toneClass}`}>{currency(value)}</div>
    </Card>
  );
}
