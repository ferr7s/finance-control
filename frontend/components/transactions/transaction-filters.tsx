"use client";

import { Search } from "lucide-react";

import { Input } from "@/components/ui/input";

export function TransactionFilters({ onSearch }: { onSearch: (value: string) => void }) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-2.5 text-slate-500" size={16} />
        <Input className="pl-9" placeholder="Filtrar por descrição, provedor, tipo ou categoria" onChange={(event) => onSearch(event.target.value)} />
      </div>
    </div>
  );
}
