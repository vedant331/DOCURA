import { useState } from "react";
import { Pencil } from "lucide-react";

import type { AttributeValueResponse } from "@/lib/api";
import { attributeLabel } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { ConfidenceIndicator } from "@/components/understanding/ConfidenceIndicator";
import { CorrectionDialog } from "@/components/understanding/CorrectionDialog";
import { SourceBadge } from "@/components/understanding/SourceBadge";
import { SensitivityBadge, SensitiveValue } from "@/components/understanding/SensitivityBadge";
import { StatusBadge } from "@/components/system/StatusBadge";

// One attribute, rendered from real record data (§9/§10/§13). Shows the value (masked if
// sensitive), its confidence, its source(s), a sensitivity tier (unclassified until
// G-14/A-5), a conflict indicator when documents disagree, and a correction action.
export function AttributeRow({
  attribute,
  docNameById = {},
}: {
  attribute: AttributeValueResponse;
  docNameById?: Record<string, string>;
}) {
  const [correcting, setCorrecting] = useState(false);
  const label = attributeLabel(attribute.canonical_identifier);
  const firstConfidence = attribute.observations[0]?.confidence ?? null;

  return (
    <div className="flex flex-col gap-2 border-b border-border py-4 last:border-b-0 sm:flex-row sm:items-start sm:justify-between">
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="label-system">{label}</span>
          <SensitivityBadge tier="unclassified" />
          {attribute.is_ambiguous ? <StatusBadge status="conflict" /> : null}
        </div>

        <div className="mt-1.5 text-sm">
          {attribute.is_ambiguous ? (
            <span className="text-muted-foreground">Multiple values — resolution required</span>
          ) : attribute.value !== null ? (
            <SensitiveValue value={attribute.value} tier="unclassified" />
          ) : (
            <span className="inline-flex items-center gap-2 text-muted-foreground">
              <StatusBadge status="missing" /> not on record
            </span>
          )}
        </div>

        <div className="mt-2 flex flex-wrap items-center gap-2">
          {attribute.observations.map((o, i) => (
            <SourceBadge key={i} documentId={o.document_id} filename={docNameById[o.document_id]} page={o.page_number} />
          ))}
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-3">
        <ConfidenceIndicator confidence={firstConfidence} />
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCorrecting(true)}
          aria-label={`Correct ${label}`}
        >
          <Pencil className="size-3.5" aria-hidden />
          Correct
        </Button>
      </div>

      <CorrectionDialog
        open={correcting}
        onOpenChange={setCorrecting}
        canonicalIdentifier={attribute.canonical_identifier}
        currentValue={attribute.value}
      />
    </div>
  );
}
