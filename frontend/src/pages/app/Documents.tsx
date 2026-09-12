import { useMemo, useState } from "react";
import { UploadCloud } from "lucide-react";

import * as api from "@/lib/api";
import type { DocumentResponse } from "@/lib/api";
import { useAsync } from "@/hooks/useAsync";
import { PageHeader } from "@/components/app/PageHeader";
import { Button } from "@/components/ui/button";
import { DocumentTable } from "@/components/documents/DocumentTable";
import { UploadDialog } from "@/components/documents/UploadDialog";
import { ConfirmationDialog } from "@/components/system/ConfirmationDialog";
import { EmptyState, ErrorState, LoadingState } from "@/components/system/states";

type Sort = "recent" | "name" | "status";

// /app/documents — the vault (§7). List, upload, sort, reprocess, delete (with confirm).
export default function DocumentsPage() {
  const docs = useAsync(() => api.listDocuments());
  const limits = useAsync(() => api.getUploadLimits());
  const [uploadOpen, setUploadOpen] = useState(false);
  const [sort, setSort] = useState<Sort>("recent");
  const [toDelete, setToDelete] = useState<DocumentResponse | null>(null);

  const documents = docs.data?.documents ?? [];
  const sorted = useMemo(() => {
    const copy = [...documents];
    if (sort === "name") copy.sort((a, b) => a.original_filename.localeCompare(b.original_filename));
    else if (sort === "status") copy.sort((a, b) => a.status.localeCompare(b.status));
    else copy.sort((a, b) => b.created_at.localeCompare(a.created_at));
    return copy;
  }, [documents, sort]);

  const reprocess = async (d: DocumentResponse) => {
    await api.reprocessDocument(d.id);
    docs.reload();
  };

  return (
    <>
      <PageHeader
        eyebrow="Vault"
        title="Documents"
        description="Every document you have stored, with its type, status, and original."
        actions={
          <Button variant="primary" onClick={() => setUploadOpen(true)}>
            <UploadCloud className="size-4" aria-hidden /> Upload
          </Button>
        }
      />

      {docs.status === "loading" ? (
        <LoadingState label="Loading documents" />
      ) : docs.status === "error" ? (
        <ErrorState message={docs.error ?? undefined} onRetry={docs.reload} />
      ) : documents.length === 0 ? (
        <EmptyState
          title="No documents yet"
          description="Upload a PDF, JPG, or PNG to get started."
          action={
            <Button variant="primary" onClick={() => setUploadOpen(true)}>
              <UploadCloud className="size-4" aria-hidden /> Upload documents
            </Button>
          }
        />
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="font-mono text-[11px] uppercase tracking-[0.15em] text-muted-foreground">
              {documents.length} document{documents.length === 1 ? "" : "s"}
            </p>
            <label className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.15em] text-muted-foreground">
              Sort
              <select
                value={sort}
                onChange={(e) => setSort(e.target.value as Sort)}
                className="border border-border bg-surface px-2 py-1 text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="recent">Most recent</option>
                <option value="name">Name</option>
                <option value="status">Status</option>
              </select>
            </label>
          </div>
          <DocumentTable documents={sorted} onReprocess={reprocess} onDelete={setToDelete} />
        </div>
      )}

      <UploadDialog open={uploadOpen} onOpenChange={setUploadOpen} limits={limits.data} onUploaded={docs.reload} />

      <ConfirmationDialog
        open={toDelete !== null}
        onOpenChange={(o) => (o ? null : setToDelete(null))}
        title="Delete this document?"
        description={
          toDelete
            ? `"${toDelete.original_filename}" and any information extracted from it will be removed. This cannot be undone here.`
            : ""
        }
        confirmLabel="Delete"
        destructive
        onConfirm={async () => {
          if (!toDelete) return;
          await api.deleteDocument(toDelete.id);
          setToDelete(null);
          docs.reload();
        }}
      />
    </>
  );
}
