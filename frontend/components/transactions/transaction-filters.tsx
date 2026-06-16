"use client";

import { RotateCcw, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { TransactionQueryFilters } from "@/types";

type TransactionFiltersProps = {
  filters: TransactionQueryFilters;
  categoryOptions: string[];
  providerOptions: string[];
  typeOptions: string[];
  loading: boolean;
  onChange: (filters: TransactionQueryFilters) => void;
  onApply: () => void | Promise<void>;
  onReset: () => void | Promise<void>;
};

function updateFilter(filters: TransactionQueryFilters, key: keyof TransactionQueryFilters, value: string) {
  return {
    ...filters,
    [key]: value || undefined
  };
}

export function TransactionFilters({
  filters,
  categoryOptions,
  providerOptions,
  typeOptions,
  loading,
  onChange,
  onApply,
  onReset
}: TransactionFiltersProps) {
  return (
    <form
      className="grid gap-3 lg:grid-cols-[minmax(220px,1.3fr)_repeat(5,minmax(130px,1fr))_auto_auto]"
      onSubmit={(event) => {
        event.preventDefault();
        onApply();
      }}
    >
      <div className="relative">
        <Search className="absolute left-3 top-2.5 text-slate-500" size={16} />
        <Input
          className="pl-9"
          placeholder="Descrição ou estabelecimento"
          value={filters.query || ""}
          onChange={(event) => onChange(updateFilter(filters, "query", event.target.value))}
        />
      </div>
      <Input type="date" value={filters.start_date || ""} onChange={(event) => onChange(updateFilter(filters, "start_date", event.target.value))} />
      <Input type="date" value={filters.end_date || ""} onChange={(event) => onChange(updateFilter(filters, "end_date", event.target.value))} />
      <select
        className="h-9 rounded-md border border-border bg-[#0f1620] px-3 text-sm text-slate-100 outline-none transition focus:border-accent"
        value={filters.category || ""}
        onChange={(event) => onChange(updateFilter(filters, "category", event.target.value))}
      >
        <option value="">Categoria</option>
        {categoryOptions.map((category) => (
          <option key={category} value={category}>
            {category}
          </option>
        ))}
      </select>
      <select
        className="h-9 rounded-md border border-border bg-[#0f1620] px-3 text-sm text-slate-100 outline-none transition focus:border-accent"
        value={filters.provider || ""}
        onChange={(event) => onChange(updateFilter(filters, "provider", event.target.value))}
      >
        <option value="">Provedor</option>
        {providerOptions.map((provider) => (
          <option key={provider} value={provider}>
            {provider}
          </option>
        ))}
      </select>
      <select
        className="h-9 rounded-md border border-border bg-[#0f1620] px-3 text-sm text-slate-100 outline-none transition focus:border-accent"
        value={filters.type || ""}
        onChange={(event) => onChange(updateFilter(filters, "type", event.target.value))}
      >
        <option value="">Tipo</option>
        {typeOptions.map((type) => (
          <option key={type} value={type}>
            {type}
          </option>
        ))}
      </select>
      <Button type="submit" disabled={loading}>
        <Search size={16} />
        Filtrar
      </Button>
      <Button type="button" className="bg-transparent text-slate-100 hover:bg-slate-800" disabled={loading} onClick={onReset}>
        <RotateCcw size={16} />
        Limpar
      </Button>
    </form>
  );
}
