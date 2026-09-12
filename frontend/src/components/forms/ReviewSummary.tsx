import { ConfidenceIndicator } from "@/components/understanding/ConfidenceIndicator";
import { StatusBadge, type Status } from "@/components/system/StatusBadge";
import { EmptyState } from "@/components/system/states";

// Final review (§26). Outstanding blockers are shown FIRST, then the per-field review and
// the attachments. Purely presentational over supplied data — it never claims completeness
// the session state does not confirm.

export interface OutstandingItem {
  kind: Status;
  label: string;
  detail?: string;
}
export interface ReviewFieldEntry {
  label: string;
  value?: string | null;
  source?: string | null;
  confidence?: number | null;
  method?: string; // automated | answered | approved | user-entered
  status: Status;
}
export interface ReviewAttachment {
  filename: string;
  targetField: string;
  source?: string | null;
  constraints?: string | null;
}

export function ReviewSummary({
  outstanding,
  fields,
  attachments,
}: {
  outstanding: OutstandingItem[];
  fields: ReviewFieldEntry[];
  attachments: ReviewAttachment[];
}) {
  return (
    <div className="space-y-8">
      {/* Outstanding — first and prominent (§26). */}
      <section aria-labelledby="rev-outstanding">
        <h3 id="rev-outstanding" className="mb-3 text-sm font-semibold text-foreground">
          Outstanding items
        </h3>
        {outstanding.length === 0 ? (
          <div className="border border-emerald-500/40 bg-emerald-500/5 px-4 py-3 text-sm text-emerald-200">
            No outstanding blockers.
          </div>
        ) : (
          <ul className="space-y-2">
            {outstanding.map((o, i) => (
              <li key={i} className="flex flex-wrap items-center gap-3 border border-amber-500/40 bg-amber-500/5 px-3 py-2">
                <StatusBadge status={o.kind} label={o.label} />
                {o.detail ? <span className="text-sm text-muted-foreground">{o.detail}</span> : null}
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Field review. */}
      <section aria-labelledby="rev-fields">
        <h3 id="rev-fields" className="mb-3 text-sm font-semibold text-foreground">
          Fields
        </h3>
        {fields.length === 0 ? (
          <EmptyState title="No fields to review" description="Field data appears here once a form session has run." />
        ) : (
          <ul className="divide-y divide-border border border-border bg-surface/30">
            {fields.map((f, i) => (
              <li key={i} className="flex flex-col gap-2 p-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-medium text-foreground">{f.label}</span>
                    {f.method ? (
                      <span className="font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">{f.method}</span>
                    ) : null}
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">{f.value ?? "—"}</p>
                  {f.source ? <p className="mt-0.5 font-mono text-[10px] text-muted-foreground">source: {f.source}</p> : null}
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <ConfidenceIndicator confidence={f.confidence ?? null} />
                  <StatusBadge status={f.status} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Attachments. */}
      <section aria-labelledby="rev-attach">
        <h3 id="rev-attach" className="mb-3 text-sm font-semibold text-foreground">
          Attachments
        </h3>
        {attachments.length === 0 ? (
          <EmptyState title="No attachments" description="Prepared documents appear here against the field that receives them." />
        ) : (
          <ul className="space-y-2">
            {attachments.map((a, i) => (
              <li key={i} className="flex flex-wrap items-center justify-between gap-2 border border-border bg-surface/40 px-3 py-2">
                <span className="truncate text-sm text-foreground">{a.filename}</span>
                <span className="font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">→ {a.targetField}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
