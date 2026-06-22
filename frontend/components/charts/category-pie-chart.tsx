"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import type { CategoryBreakdownItem } from "@/types";
import { asNumber } from "@/lib/api";
import { currency } from "@/lib/formatters";

const MONO_SHADES = ["#ffffff", "#cccccc", "#aaaaaa", "#888888", "#666666", "#444444", "#333333", "#222222"];

export function CategoryPieChart({ data }: { data: CategoryBreakdownItem[] }) {
  const chartData = data.map((item) => ({ name: item.category, value: asNumber(item.amount) }));
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={58} outerRadius={92} paddingAngle={1} strokeWidth={0}>
            {chartData.map((entry, index) => (
              <Cell key={entry.name} fill={MONO_SHADES[index % MONO_SHADES.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => currency(Number(value))}
            contentStyle={{ background: "#0a0a0a", border: "1px solid #222", fontSize: 11 }}
            labelStyle={{ color: "#fff" }}
            itemStyle={{ color: "#aaa" }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
