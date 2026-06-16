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
          <CartesianGrid stroke="#243244" vertical={false} />
          <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
          <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(value) => `R$${Math.round(Number(value) / 1000)}k`} />
          <Tooltip formatter={(value) => currency(Number(value))} contentStyle={{ background: "#0f1620", border: "1px solid #273241" }} />
          <Line dataKey="patrimonio" stroke="#2dd4bf" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
