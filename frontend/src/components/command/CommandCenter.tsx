import { Link } from "react-router-dom";
import { FolderOpen, UploadCloud } from "lucide-react";

import type { DocumentResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ChatComposer } from "@/components/command/ChatComposer";
import { ChatWorkspace } from "@/components/command/ChatWorkspace";
import { DocumentCard } from "@/components/documents/DocumentCard";
import { StatusBadge } from "@/components/system/StatusBadge";
import { EmptyState } from "@/components/system/states";

// The DOCURA command center (§5/§35): the primary post-login surface. It adapts to real
// document state — empty, processing, failed, or ready — and never pretends to analyse
// documents that do not exist or generate answers it cannot.

function DocumentEmptyState({ onUpload }: { onUpload: () => void }) {
  return (
    <div className="space-y-6">
      <EmptyState
        title="Document vault empty"
        description="Let's start by adding your documents. DOCURA reads them so your details become reusable across forms."
        icon={<FolderOpen className="size-8" />}
        action={
          <div className="flex flex-wrap items-center justify-center gap-2">
            <Button variant="primary" onClick={onUpload}>
              <UploadCloud className="size-4" aria-hidden /> Upload documents
            </Button>
            <Button asChild variant="outline">
              <Link to="/app/documents">Open document vault</Link>
            </Button>
          </div>
        }
      />
      {/* The composer is present but honest: nothing to analyse yet. */}
      <ChatComposer onSubmit={() => {}} disabled placeholder="Upload a document to begin..." />
    </div>
  );
}

export function CommandCenter({
  documents,
  onUpload,
}: {
  documents: DocumentResponse[];
  onUpload: () => void;
}) {
  if (documents.length === 0) return <DocumentEmptyState onUpload={onUpload} />;

  const processing = documents.filter((d) => d.status === "processing" || d.status === "queued");
  const failed = documents.filter((d) => d.status === "failed");
  const ready = documents.filter((d) => d.status === "ready" || d.status === "needs_review");

  return (
    <div className="space-y-6">
      {/* State summary from real backend status. */}
      <div className="grid gap-px overflow-hidden border border-border bg-border sm:grid-cols-4">
        {[
          { k: "Documents", v: String(documents.length) },
          { k: "Ready", v: String(ready.length) },
          { k: "Processing", v: String(processing.length) },
          { k: "Failed", v: String(failed.length) },
        ].map((c) => (
          <div key={c.k} className="bg-surface/50 p-4">
            <p className="label-system">{c.k}</p>
            <p className="mt-1 text-xl font-bold text-foreground">{c.v}</p>
          </div>
        ))}
      </div>

      {/* STATE C — processing (real state, no invented percentages). */}
      {processing.length > 0 ? (
        <div className="flex flex-wrap items-center gap-3 border border-sky-500/30 bg-sky-500/5 px-4 py-3">
          <StatusBadge status="processing" label="Document processing" />
          <span className="text-sm text-muted-foreground">
            {processing.map((d) => d.original_filename).slice(0, 3).join(", ")}
            {processing.length > 3 ? ` +${processing.length - 3} more` : ""}
          </span>
        </div>
      ) : null}

      {/* STATE D — failed (reason + actions; original never hidden). */}
      {failed.length > 0 ? (
        <div className="space-y-2 border border-destructive/40 bg-destructive/5 p-4">
          <StatusBadge status="failed" label="Processing failed" />
          <div className="grid gap-2 sm:grid-cols-2">
            {failed.slice(0, 4).map((d) => (
              <DocumentCard key={d.id} document={d} />
            ))}
          </div>
        </div>
      ) : null}

      {/* STATE B — documents exist: the command/chat interface. */}
      <section aria-label="Command" className="border border-border bg-surface/30 p-4 sm:p-6">
        <ChatWorkspace contextCount={documents.length} />
      </section>
    </div>
  );
}
