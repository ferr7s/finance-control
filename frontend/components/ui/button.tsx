import { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Button({ className, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        "inline-flex h-9 items-center justify-center gap-2 border border-white/20 bg-white/10 px-3 text-xs font-medium uppercase tracking-widest text-white transition hover:bg-white hover:text-black disabled:cursor-not-allowed disabled:opacity-40",
        className
      )}
      {...props}
    />
  );
}
