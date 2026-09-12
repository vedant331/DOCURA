import type { SupportingObservationResponse } from "@/lib/api";
import { ConfidenceIndicator } from "@/components/understanding/ConfidenceIndicator";
import { SourceBadge } from "@/components/understanding/SourceBadge";

// The provenance chain for one attribute (§10): every supporting observation with its
// value, source document + page/region, and confidence. Renders only what the backend
// carries; region is shown when the engine reported one.
export function ProvenancePanel({
  observations,
  docNameById = {},
}: {
  observations: SupportingObservationResponse[];
  docNameById?: Record<string, string>;
}) {
  if (observations.length === 0) {
    return (
      <p className="font-mono text-[11px] uppercase tracking-[0.15em] text-muted-foreground">
        No supporting observations
      </p>
    );
  }
  return (
    <ul className="space-y-2">
      {observations.map((o, i) => (
        <li key={`${o.document_id}-${i}`} className="flex flex-wrap items-center justify-between gap-2 border border-border bg-surface/40 px-3 py-2">
          <div className="min-w-0">
            <p className="truncate text-sm text-foreground">{o.value}</p>
            <div className="mt-1 flex flex-wrap items-center gap-2">
              <SourceBadge documentId={o.document_id} filename={docNameById[o.document_id]} page={o.page_number} />
              {o.region ? (
                <span className="font-mono text-[10px] text-muted-foreground/70">region ✓</span>
              ) : null}
            </div>
          </div>
          <ConfidenceIndicator confidence={o.confidence} />
        </li>
      ))}
    </ul>
  );
}
