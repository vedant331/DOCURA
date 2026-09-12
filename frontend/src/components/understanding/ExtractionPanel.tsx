import type { AttributeValueResponse } from "@/lib/api";
import { AttributeRow } from "@/components/record/AttributeRow";
import { ConflictPanel } from "@/components/understanding/ConflictPanel";
import { EmptyState } from "@/components/system/states";

// The document-understanding panel (§9). Lists the attributes DOCURA extracted (filtered
// to this document by the caller), with conflicts surfaced separately. When extraction has
// produced nothing — the expected state while the OCR engine is unconfigured (M8 blocked)
// — it shows an honest empty state rather than inventing values.
export function ExtractionPanel({
  attributes,
  docNameById = {},
  emptyHint,
}: {
  attributes: AttributeValueResponse[];
  docNameById?: Record<string, string>;
  emptyHint?: string;
}) {
  if (attributes.length === 0) {
    return (
      <EmptyState
        title="No extracted information yet"
        description={
          emptyHint ??
          "DOCURA has not extracted structured information from this document. Extraction runs once the OCR engine is configured; the original file is always available above."
        }
      />
    );
  }

  const conflicts = attributes.filter((a) => a.is_ambiguous);
  const settled = attributes.filter((a) => !a.is_ambiguous);

  return (
    <div className="space-y-4">
      {conflicts.map((a) => (
        <ConflictPanel key={a.canonical_identifier} attribute={a} docNameById={docNameById} />
      ))}
      {settled.length > 0 ? (
        <div className="border border-border bg-surface/30 px-4">
          {settled.map((a) => (
            <AttributeRow key={a.canonical_identifier} attribute={a} docNameById={docNameById} />
          ))}
        </div>
      ) : null}
    </div>
  );
}
