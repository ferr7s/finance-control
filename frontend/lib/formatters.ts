export function currency(value: number | string | null | undefined) {
  const amount = Number(value ?? 0);
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL"
  }).format(amount);
}

export function shortDate(value: string) {
  const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (dateOnly) {
    return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "2-digit", year: "2-digit" }).format(
      new Date(Number(dateOnly[1]), Number(dateOnly[2]) - 1, Number(dateOnly[3]))
    );
  }
  return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "2-digit", year: "2-digit" }).format(
    new Date(value)
  );
}

export function referenceMonth(value: string) {
  const [year, month] = value.slice(0, 7).split("-").map(Number);
  return new Intl.DateTimeFormat("pt-BR", { month: "long", year: "numeric" }).format(new Date(year, month - 1, 1));
}

export function percent(value: number) {
  return `${value.toFixed(1)}%`;
}
