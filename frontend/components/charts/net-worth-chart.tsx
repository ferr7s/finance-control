"use client";

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { asNumber } from "@/lib/api";
import { currency } from "@/lib/formatters";
import type { MonthlyCashflowPoint } from "@/types";

export function NetWorthChart({ data, startingBalance }: { data: MonthlyCashflowPoint[]; startingBalance: string }) {
  const chartData = data.reduce<Array<{ month: string; patrimonio: number }>>((points, item) => {
    const previousBalance = points.at(-1)?.patrimonio ?? asNumber(startingBalance);
    return [...points, { month: item.month, patrimonio: previousBalance + asNumber(item.result) }];
  }, []);

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid stroke="#1e1e1e" vertical={false} strokeDasharray="4 4" />
          <XAxis dataKey="month" stroke="#333" fontSize={10} tick={{ fill: "#555" }} tickLine={false} axisLine={false} />
          <YAxis stroke="#333" fontSize={10} tick={{ fill: "#555" }} tickLine={false} axisLine={false} tickFormatter={(v) => `R$${Math.round(Number(v) / 1000)}k`} />
          <Tooltip
            formatter={(value) => currency(Number(value))}
            contentStyle={{ background: "#0a0a0a", border: "1px solid #222", fontSize: 11 }}
            labelStyle={{ color: "#fff" }}
            itemStyle={{ color: "#aaa" }}
          />
          <Line dataKey="patrimonio" stroke="#ffffff" strokeWidth={1.5} dot={{ r: 2, fill: "#ffffff", strokeWidth: 0 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
