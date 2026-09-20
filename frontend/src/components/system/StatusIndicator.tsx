import { cn } from "@/lib/utils";

// A small dot + mono label system indicator (§28). Tone is conveyed by the label text
// too, never colour alone.
export function StatusIndicator({
  label,
  tone = "neutral",
  className,
}: {
  label: string;
  tone?: "ok" | "warn" | "error" | "neutral";
  className?: string;
}) {
  const dot = {
    ok: "bg-success [box-shadow:0_0_8px_hsl(var(--success))]",
    warn: "bg-warning [box-shadow:0_0_8px_hsl(var(--warning))]",
    error: "bg-destructive [box-shadow:0_0_8px_hsl(var(--destructive))]",
    neutral: "bg-mercury [box-shadow:0_0_8px_hsl(var(--mercury))]",
  }[tone];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-muted-foreground",
        className,
      )}
    >
      <span aria-hidden className={cn("inline-block size-1.5 rounded-full", dot)} />
      {label}
    </span>
  );
}
