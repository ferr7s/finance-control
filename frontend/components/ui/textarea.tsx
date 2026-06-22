import { TextareaHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-24 w-full border border-border bg-black px-3 py-2 text-xs text-white outline-none transition placeholder:text-white/30 focus:border-white/40",
        className
      )}
      {...props}
    />
  );
}
