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
    default: "text-slate-100",
    success: "text-success",
    danger: "text-danger",
    warning: "text-warning"
  }[tone];
  return (
    <Card className="min-h-28">
      <div className="flex items-center justify-between gap-3 text-sm text-slate-400">
        <span>{title}</span>
        {icon}
      </div>
      <div className={`mt-4 text-2xl font-semibold ${toneClass}`}>{currency(value)}</div>
    </Card>
  );
}
