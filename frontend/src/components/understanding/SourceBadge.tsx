import { Link } from "react-router-dom";
import { FileText } from "lucide-react";

import { cn } from "@/lib/utils";

// Provenance chip: the source document (+ page) a value was read from (FR-OCR-007,
// AR-AST-006). Links into the document detail so the user can inspect the source. The
// filename is resolved by the caller (the record API references the document by id only).
export function SourceBadge({
  documentId,
  filename,
  page,
  className,
}: {
  documentId: string;
  filename?: string | null;
  page?: number | null;
  className?: string;
}) {
  const label = filename ?? `Document ${documentId.slice(0, 8)}`;
  return (
    <Link
      to={`/documents/${documentId}`}
      className={cn(
        "inline-flex items-center gap-1.5 border border-border bg-surface/50 px-2 py-0.5 font-mono text-[10px] text-muted-foreground transition-colors hover:border-mercury/40 hover:text-foreground",
        className,
      )}
    >
      <FileText className="size-3" aria-hidden />
      <span className="max-w-[160px] truncate">{label}</span>
      {page ? <span className="text-muted-foreground/70">· p{page}</span> : null}
    </Link>
  );
}
