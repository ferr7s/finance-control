import { cn } from "@/lib/utils";

export function Badge({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn("inline-flex items-center border border-white/20 px-2 py-0.5 text-xs uppercase tracking-widest text-white/60", className)}
      {...props}
    />
  );
}
