import { Link } from "react-router-dom";
import { Eye, RotateCw, Trash2 } from "lucide-react";

import type { DocumentResponse } from "@/lib/api";
import { formatBytes, formatDate } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { DocumentCard } from "@/components/documents/DocumentCard";
import { DocumentStatus } from "@/components/documents/DocumentStatus";

// The vault list (§7). A table on wider screens, cards when stacked (§30). Sortable by the
// caller (sort controls live on the page). Reuses DocumentCard for the responsive variant.
export function DocumentTable({
  documents,
  onReprocess,
  onDelete,
}: {
  documents: DocumentResponse[];
  onReprocess?: (d: DocumentResponse) => void;
  onDelete?: (d: DocumentResponse) => void;
}) {
  return (
    <>
      {/* Mobile / stacked */}
      <div className="grid gap-3 sm:grid-cols-2 lg:hidden">
        {documents.map((d) => (
          <DocumentCard key={d.id} document={d} onReprocess={onReprocess} onDelete={onDelete} />
        ))}
      </div>

      {/* Desktop table */}
      <div className="hidden overflow-x-auto border border-border lg:block">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-border bg-surface/50">
            <tr className="font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
              <th scope="col" className="px-4 py-3 font-normal">Document</th>
              <th scope="col" className="px-4 py-3 font-normal">Type</th>
              <th scope="col" className="px-4 py-3 font-normal">Status</th>
              <th scope="col" className="px-4 py-3 font-normal">Added</th>
              <th scope="col" className="px-4 py-3 font-normal">Size</th>
              <th scope="col" className="px-4 py-3 text-right font-normal">Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((d) => {
              const canReprocess = d.status === "failed" || d.status === "needs_review";
              return (
                <tr key={d.id} className="border-b border-border last:border-b-0 hover:bg-surface/40">
                  <td className="max-w-[280px] px-4 py-3">
                    <Link to={`/app/documents/${d.id}`} className="truncate font-medium text-foreground hover:underline" title={d.original_filename}>
                      {d.original_filename}
                    </Link>
                  </td>
                  <td className="px-4 py-3 font-mono text-[11px] text-muted-foreground">{d.document_type}</td>
                  <td className="px-4 py-3"><DocumentStatus document={d} showReason={false} /></td>
                  <td className="px-4 py-3 text-muted-foreground">{formatDate(d.created_at)}</td>
                  <td className="px-4 py-3 text-muted-foreground">{formatBytes(d.byte_size)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-1">
                      <Button asChild variant="ghost" size="icon" aria-label={`View ${d.original_filename}`}>
                        <Link to={`/app/documents/${d.id}`}><Eye className="size-4" aria-hidden /></Link>
                      </Button>
                      {canReprocess && onReprocess ? (
                        <Button variant="ghost" size="icon" onClick={() => onReprocess(d)} aria-label={`Reprocess ${d.original_filename}`}>
                          <RotateCw className="size-4" aria-hidden />
                        </Button>
                      ) : null}
                      {onDelete ? (
                        <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive" onClick={() => onDelete(d)} aria-label={`Delete ${d.original_filename}`}>
                          <Trash2 className="size-4" aria-hidden />
                        </Button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}
