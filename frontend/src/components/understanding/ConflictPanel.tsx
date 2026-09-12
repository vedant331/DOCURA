import type { AttributeValueResponse } from "@/lib/api";
import { attributeLabel } from "@/lib/format";
import { ConfidenceIndicator } from "@/components/understanding/ConfidenceIndicator";
import { SourceBadge } from "@/components/understanding/SourceBadge";
import { StatusBadge } from "@/components/system/StatusBadge";
import { NotConnected } from "@/components/system/states";

// Conflict presentation (§12): when the user's own documents disagree on an attribute,
// show every competing value with its source. DOCURA does NOT pick newest/most-frequent/
// preferred/first — the user decides. Resolution is a backend capability that does not
// exist yet (record API is read-only), so the choose controls are an honest seam.
export function ConflictPanel({
  attribute,
  docNameById = {},
}: {
  attribute: AttributeValueResponse;
  docNameById?: Record<string, string>;
}) {
  // Group observations by distinct value — each is a candidate the user could choose.
  const byValue = new Map<string, typeof attribute.observations>();
  for (const o of attribute.observations) {
    if (!byValue.has(o.value)) byValue.set(o.value, []);
    byValue.get(o.value)!.push(o);
  }
  const candidates = [...byValue.entries()];

  return (
    <section aria-label="Conflict" className="border border-orange-500/40 bg-orange-500/5 p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div>
          <StatusBadge status="conflict" label="Conflict detected" />
          <p className="mt-2 text-sm text-foreground">
            Your documents disagree on <span className="font-semibold">{attributeLabel(attribute.canonical_identifier)}</span>.
          </p>
        </div>
      </div>

      <ul className="space-y-2">
        {candidates.map(([value, obs], i) => (
          <li key={value} className="flex flex-wrap items-center justify-between gap-2 border border-border bg-surface/50 px-3 py-2">
            <div className="min-w-0">
              <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">Candidate {String.fromCharCode(65 + i)}</p>
              <p className="mt-0.5 truncate text-sm text-foreground">{value}</p>
              <div className="mt-1 flex flex-wrap items-center gap-2">
                {obs.map((o, j) => (
                  <SourceBadge key={j} documentId={o.document_id} filename={docNameById[o.document_id]} page={o.page_number} />
                ))}
              </div>
            </div>
            <ConfidenceIndicator confidence={obs[0]?.confidence ?? null} />
          </li>
        ))}
      </ul>

      <NotConnected
        className="mt-3"
        title="Resolution not yet connected"
        description="Choosing an authoritative value needs a backend resolution endpoint that does not exist yet. DOCURA will never resolve this automatically."
      />
    </section>
  );
}
