import type { MatchStatusKind, UploadFieldMatch } from "@/components/forms/types";
import { ConfidenceIndicator } from "@/components/understanding/ConfidenceIndicator";
import { StatusBadge, type Status } from "@/components/system/StatusBadge";

// Document-matching UI for upload fields (§22). Shows the field's required type/constraints,
// the matched candidate(s) with confidence, and the match state. When multiple documents
// are plausible it asks the user — it never auto-selects (BR-003).

const MATCH_STATUS: Record<MatchStatusKind, Status> = {
  matched: "matched",
  multiple: "multiple",
  missing: "missing",
  preparing: "preparing",
  ready: "ready",
  blocked: "blocked",
  quality_loss: "quality_loss",
  unresolved: "unknown",
};

export function MatchingPanel({
  match,
  onChoose,
}: {
  match: UploadFieldMatch;
  onChoose?: (documentId: string) => void;
}) {
  return (
    <section className="border border-border bg-surface/30 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="label-system">Upload field</p>
          <p className="mt-1 font-mono text-sm text-foreground">{match.fieldId}</p>
        </div>
        <StatusBadge status={MATCH_STATUS[match.status]} />
      </div>

      {match.requiredType || match.constraints ? (
        <p className="mt-2 font-mono text-[11px] text-muted-foreground">
          {match.requiredType ? `type: ${match.requiredType}  ` : ""}
          {match.constraints?.format ? `format: ${match.constraints.format}  ` : ""}
          {match.constraints?.maxSize ? `max: ${match.constraints.maxSize}  ` : ""}
          {match.constraints?.dimensions ? `dims: ${match.constraints.dimensions}` : ""}
        </p>
      ) : null}

      {match.candidates && match.candidates.length > 0 ? (
        <ul className="mt-3 space-y-2">
          {match.candidates.map((c) => (
            <li key={c.documentId} className="flex items-center justify-between gap-2 border border-border bg-surface/50 px-3 py-2">
              <span className="truncate text-sm text-foreground">{c.filename ?? c.documentId}</span>
              <div className="flex items-center gap-3">
                <ConfidenceIndicator confidence={c.confidence ?? null} />
                {match.status === "multiple" && onChoose ? (
                  <button
                    type="button"
                    onClick={() => onChoose(c.documentId)}
                    className="font-mono text-[10px] uppercase tracking-[0.15em] text-foreground underline underline-offset-4 hover:text-mercury"
                  >
                    Choose
                  </button>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      ) : null}

      {match.reason ? <p className="mt-2 text-sm text-muted-foreground">{match.reason}</p> : null}
    </section>
  );
}
