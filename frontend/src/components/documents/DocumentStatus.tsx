import type { DocumentResponse } from "@/lib/api";
import { StatusBadge, documentStatusToStatus } from "@/components/system/StatusBadge";

// Document processing status (FR-UPL-005) + the failure reason where present (FR-OCR-009).
export function DocumentStatus({ document, showReason = true }: { document: DocumentResponse; showReason?: boolean }) {
  return (
    <span className="inline-flex flex-wrap items-center gap-2">
      <StatusBadge status={documentStatusToStatus(document.status)} />
      {showReason && document.status === "failed" && document.failure_reason ? (
        <span className="font-mono text-[10px] text-destructive">{document.failure_reason}</span>
      ) : null}
    </span>
  );
}
