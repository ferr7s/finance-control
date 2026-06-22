"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { MonthlyCashflowPoint } from "@/types";
import { asNumber } from "@/lib/api";
import { currency } from "@/lib/formatters";

export function CashflowChart({ data }: { data: MonthlyCashflowPoint[] }) {
  const chartData = data.map((item) => ({
    month: item.month,
    entradas: asNumber(item.income),
    saídas: asNumber(item.expenses)
  }));
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} barGap={2}>
          <CartesianGrid stroke="#1e1e1e" vertical={false} strokeDasharray="4 4" />
          <XAxis dataKey="month" stroke="#333" fontSize={10} tick={{ fill: "#555" }} tickLine={false} axisLine={false} />
          <YAxis stroke="#333" fontSize={10} tick={{ fill: "#555" }} tickLine={false} axisLine={false} tickFormatter={(v) => `R$${Number(v) / 1000}k`} />
          <Tooltip
            formatter={(value) => currency(Number(value))}
            contentStyle={{ background: "#0a0a0a", border: "1px solid #222", fontSize: 11 }}
            labelStyle={{ color: "#fff" }}
            itemStyle={{ color: "#aaa" }}
          />
          <Bar dataKey="entradas" fill="#ffffff" radius={0} />
          <Bar dataKey="saídas" fill="#444444" radius={0} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
