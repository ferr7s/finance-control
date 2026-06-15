import { InputHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-9 w-full rounded-md border border-border bg-[#0f1620] px-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-accent",
        className
      )}
      {...props}
    />
  );
}
