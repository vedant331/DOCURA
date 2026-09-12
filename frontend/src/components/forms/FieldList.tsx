import type { DetectedField, FieldStatusKind } from "@/components/forms/types";
import { ConfidenceIndicator } from "@/components/understanding/ConfidenceIndicator";
import { DeclarationWarning } from "@/components/forms/DeclarationWarning";
import { StatusBadge, type Status } from "@/components/system/StatusBadge";

// Field interpretation UI (§19/§21). Each detected field shows its label, type,
// required/optional, recognised meaning, confidence, proposed value, source, and status.
// Unknown fields stay visibly untouched; declarations get the special user-action
// treatment. Fill categories (§21) are conveyed by the status badge, never implying every
// field will be auto-filled.

const FIELD_STATUS: Record<FieldStatusKind, Status> = {
  matched: "matched",
  available: "ready",
  unknown: "unknown",
  ambiguous: "ambiguous",
  conflict: "conflict",
  requires_user: "action_required",
  blocked: "blocked",
  missing: "missing",
  declaration: "declaration",
};

export function FieldStatus({ status }: { status: FieldStatusKind }) {
  return <StatusBadge status={FIELD_STATUS[status]} />;
}

export function FieldList({ fields }: { fields: DetectedField[] }) {
  return (
    <ul className="divide-y divide-border border border-border bg-surface/30">
      {fields.map((f) => (
        <li key={f.fieldId} className="p-4">
          {f.isDeclaration || f.status === "declaration" ? (
            <DeclarationWarning fieldLabel={f.meaning ?? f.fieldId} />
          ) : (
            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-medium text-foreground">{f.meaning ?? f.fieldId}</span>
                  <span className="font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
                    {f.type}
                    {f.required ? " · required" : " · optional"}
                  </span>
                </div>
                {f.proposedValue ? (
                  <p className="mt-1 text-sm text-muted-foreground">
                    Proposed: <span className="text-foreground">{f.proposedValue}</span>
                  </p>
                ) : null}
                {f.status === "unknown" ? (
                  <p className="mt-1 font-mono text-[11px] text-muted-foreground">Left untouched — meaning not determined.</p>
                ) : null}
                {f.source ? <p className="mt-1 font-mono text-[11px] text-muted-foreground">source: {f.source}</p> : null}
              </div>
              <div className="flex shrink-0 items-center gap-3">
                <ConfidenceIndicator confidence={f.confidence ?? null} />
                <FieldStatus status={f.status} />
              </div>
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}
