import { Link } from "react-router-dom";
import { Eye, RotateCw, Trash2 } from "lucide-react";

import type { DocumentResponse } from "@/lib/api";
import { formatBytes, formatDate } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { DocumentStatus } from "@/components/documents/DocumentStatus";

// One document as a card (§7). Type, filename, date, size, status + failure reason, and
// actions: view, reprocess (when failed/needs review), delete. The original is never
// hidden because processing failed.
export function DocumentCard({
  document,
  onReprocess,
  onDelete,
}: {
  document: DocumentResponse;
  onReprocess?: (d: DocumentResponse) => void;
  onDelete?: (d: DocumentResponse) => void;
}) {
  const canReprocess = document.status === "failed" || document.status === "needs_review";
  return (
    <article className="flex flex-col gap-3 border border-border bg-surface/40 p-4 transition-colors hover:border-mercury/30">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="label-system">{document.document_type}</p>
          <Link
            to={`/app/documents/${document.id}`}
            className="mt-1 block truncate text-sm font-semibold text-foreground hover:underline"
            title={document.original_filename}
          >
            {document.original_filename}
          </Link>
        </div>
      </div>

      <DocumentStatus document={document} />

      <div className="mt-auto flex items-center justify-between border-t border-border pt-3 font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
        <span>{formatDate(document.created_at)}</span>
        <span>{formatBytes(document.byte_size)}</span>
      </div>

      <div className="flex items-center gap-1">
        <Button asChild variant="ghost" size="sm">
          <Link to={`/app/documents/${document.id}`} aria-label={`View ${document.original_filename}`}>
            <Eye className="size-3.5" aria-hidden /> View
          </Link>
        </Button>
        {canReprocess && onReprocess ? (
          <Button variant="ghost" size="sm" onClick={() => onReprocess(document)} aria-label={`Reprocess ${document.original_filename}`}>
            <RotateCw className="size-3.5" aria-hidden /> Retry
          </Button>
        ) : null}
        {onDelete ? (
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto text-destructive hover:text-destructive"
            onClick={() => onDelete(document)}
            aria-label={`Delete ${document.original_filename}`}
          >
            <Trash2 className="size-3.5" aria-hidden /> Delete
          </Button>
        ) : null}
      </div>
    </article>
  );
}
