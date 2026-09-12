import { cn } from "@/lib/utils";

// Shows the extraction confidence a value was read with — the ACTUAL number the backend
// reported, never an invented one. When the engine reported none (null), that is stated
// as a distinct fact (FR-OCR-005). It deliberately does NOT bucket into HIGH/LOW: the
// automatic-action threshold is TBD (BR-001) and inventing a cutoff here would fabricate
// the evidence BR-001 depends on.
export function ConfidenceIndicator({
  confidence,
  className,
}: {
  confidence: number | null | undefined;
  className?: string;
}) {
  if (confidence === null || confidence === undefined) {
    return (
      <span className={cn("font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground", className)}>
        No confidence reported
      </span>
    );
  }
  const pct = Math.round(confidence * 100);
  return (
    <span className={cn("inline-flex items-center gap-2", className)} title={`Confidence ${pct}%`}>
      <span aria-hidden className="h-1 w-16 overflow-hidden bg-muted">
        <span className="block h-full bg-mercury" style={{ width: `${pct}%` }} />
      </span>
      <span className="font-mono text-[10px] tracking-widest text-muted-foreground">{pct}%</span>
    </span>
  );
}
