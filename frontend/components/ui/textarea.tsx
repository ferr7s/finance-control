import { TextareaHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-24 w-full rounded-md border border-border bg-[#0f1620] px-3 py-2 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-accent",
        className
      )}
      {...props}
    />
  );
}
