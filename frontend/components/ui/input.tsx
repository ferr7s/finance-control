import { InputHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-9 w-full border border-border bg-black px-3 text-xs text-white outline-none transition placeholder:text-white/30 focus:border-white/40",
        className
      )}
      {...props}
    />
  );
}
