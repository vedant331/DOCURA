import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, RotateCw, Trash2 } from "lucide-react";

import * as api from "@/lib/api";
import { useAsync } from "@/hooks/useAsync";
import { formatBytes, formatDateTime } from "@/lib/format";
import { PageHeader } from "@/components/app/PageHeader";
import { Button } from "@/components/ui/button";
import { DocumentPreview } from "@/components/documents/DocumentPreview";
import { DocumentStatus } from "@/components/documents/DocumentStatus";
import { ExtractionPanel } from "@/components/understanding/ExtractionPanel";
import { ConfirmationDialog } from "@/components/system/ConfirmationDialog";
import { ErrorState, LoadingState } from "@/components/system/states";

// /app/documents/:documentId — document inspection & understanding (§9/§10). Header +
// original preview + the understanding panel (attributes DOCURA read from THIS document,
// with provenance & confidence). The original is always shown, even when processing
// failed. All data is real; extraction is empty until the OCR engine is configured.
export default function DocumentDetailPage() {
  const { documentId = "" } = useParams();
  const navigate = useNavigate();
  const doc = useAsync(() => api.getDocument(documentId), [documentId]);
  const record = useAsync(() => api.getRecord(), [documentId]);
  const [deleting, setDeleting] = useState(false);

  if (doc.status === "loading") return <LoadingState label="Loading document" />;
  if (doc.status === "error" || !doc.data) {
    return <ErrorState message={doc.error ?? "Document not found."} onRetry={doc.reload} />;
  }

  const document = doc.data;
  const canReprocess = document.status === "failed" || document.status === "needs_review";

  // Attributes supported by an observation from THIS document (§9). The record API
  // references documents by id; we only know this document's name here.
  const attributes = (record.data?.attributes ?? []).filter((a) =>
    a.observations.some((o) => o.document_id === documentId),
  );
  const docNameById = { [documentId]: document.original_filename };

  return (
    <>
      <PageHeader
        breadcrumbs={[
          { label: "Documents", to: "/app/documents" },
          { label: document.original_filename },
        ]}
        eyebrow={document.document_type}
        title={document.original_filename}
        description={
          <span className="inline-flex flex-wrap items-center gap-3">
            <DocumentStatus document={document} />
            <span className="font-mono text-[11px] text-muted-foreground">
              {formatBytes(document.byte_size)} · added {formatDateTime(document.created_at)}
            </span>
          </span>
        }
        actions={
          <>
            <Button variant="ghost" onClick={() => navigate("/app/documents")}>
              <ArrowLeft className="size-4" aria-hidden /> Back
            </Button>
            {canReprocess ? (
              <Button
                variant="outline"
                onClick={async () => {
                  await api.reprocessDocument(document.id);
                  doc.reload();
                }}
              >
                <RotateCw className="size-4" aria-hidden /> Reprocess
              </Button>
            ) : null}
            <Button variant="destructive" onClick={() => setDeleting(true)}>
              <Trash2 className="size-4" aria-hidden /> Delete
            </Button>
          </>
        }
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <section aria-label="Original document" className="border border-border bg-surface/30">
          <DocumentPreview
            documentId={document.id}
            contentType={document.content_type}
            filename={document.original_filename}
          />
        </section>

        <section aria-labelledby="understanding-heading">
          <h2 id="understanding-heading" className="mb-3 text-sm font-semibold text-foreground">
            What DOCURA understood
          </h2>
          {record.status === "loading" ? (
            <LoadingState label="Reading record" />
          ) : record.status === "error" ? (
            <ErrorState message={record.error ?? undefined} onRetry={record.reload} />
          ) : (
            <ExtractionPanel attributes={attributes} docNameById={docNameById} />
          )}
        </section>
      </div>

      <ConfirmationDialog
        open={deleting}
        onOpenChange={setDeleting}
        title="Delete this document?"
        description={`"${document.original_filename}" and any information extracted from it will be removed. This cannot be undone here.`}
        confirmLabel="Delete"
        destructive
        onConfirm={async () => {
          await api.deleteDocument(document.id);
          navigate("/app/documents", { replace: true });
        }}
      />
    </>
  );
}
