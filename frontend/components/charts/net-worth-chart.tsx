"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";

import type { MonthlyCashflowPoint } from "@/types";
import { asNumber } from "@/lib/api";
import { currency } from "@/lib/formatters";

export function NetWorthChart({ data, startingBalance }: { data: MonthlyCashflowPoint[]; startingBalance: string }) {
  let balance = asNumber(startingBalance);
  const chartData = data.map((item) => {
    balance += asNumber(item.result);
    return { month: item.month, patrimônio: balance };
  });
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid stroke="#243244" vertical={false} />
          <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
          <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(value) => `R$${Math.round(Number(value) / 1000)}k`} />
          <Tooltip formatter={(value) => currency(Number(value))} contentStyle={{ background: "#0f1620", border: "1px solid #273241" }} />
          <Line dataKey="patrimônio" stroke="#2dd4bf" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
