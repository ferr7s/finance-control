"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import type { CategoryBreakdownItem } from "@/types";
import { asNumber } from "@/lib/api";
import { currency } from "@/lib/formatters";

const COLORS = ["#2dd4bf", "#22c55e", "#f59e0b", "#60a5fa", "#ef4444", "#a78bfa", "#f472b6", "#94a3b8"];

export function CategoryPieChart({ data }: { data: CategoryBreakdownItem[] }) {
  const chartData = data.map((item) => ({ name: item.category, value: asNumber(item.amount) }));
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={58} outerRadius={92} paddingAngle={2}>
            {chartData.map((entry, index) => (
              <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => currency(Number(value))} contentStyle={{ background: "#0f1620", border: "1px solid #273241" }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
