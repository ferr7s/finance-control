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
        <BarChart data={chartData}>
          <CartesianGrid stroke="#243244" vertical={false} />
          <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
          <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(value) => `R$${Number(value) / 1000}k`} />
          <Tooltip formatter={(value) => currency(Number(value))} contentStyle={{ background: "#0f1620", border: "1px solid #273241" }} />
          <Bar dataKey="entradas" fill="#22c55e" radius={[4, 4, 0, 0]} />
          <Bar dataKey="saídas" fill="#ef4444" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
