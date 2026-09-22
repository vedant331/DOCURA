import { Link } from "react-router-dom";
import { FolderCheck, FolderPlus, Loader2 } from "lucide-react";

import type { DocumentResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

// A compact, highlighted card in the TOP-RIGHT of the chat workspace — part of the layout,
// never a popup/modal/chat message. It shows REAL document state from listDocuments():
//   * documents exist → "Documents ready" + count + View Documents
//   * none            → "No documents uploaded" + Upload Documents
// The two states are mutually exclusive. Loading/error use explicit states, never fake counts.
export function DocumentStatusCard({
  documents,
  loading,
  className,
}: {
  documents: DocumentResponse[] | null;
  loading?: boolean;
  className?: string;
}) {
  const base = cn(
    "w-full rounded-2xl border p-3.5 sm:w-72",
    className,
  );

  if (loading || documents === null) {
    return (
      <div className={cn(base, "border-white/8 bg-surface/60")}>
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="size-4 animate-spin" aria-hidden />
          <span className="text-xs">Checking your documents…</span>
        </div>
      </div>
    );
  }

  const ready = documents.filter((d) => d.status === "ready" || d.status === "needs_review").length;

  if (documents.length === 0) {
    return (
      <div className={cn(base, "border-white/8 bg-surface/60")}>
        <div className="flex items-center gap-2">
          <span className="flex size-8 items-center justify-center rounded-lg bg-white/5 text-muted-foreground ring-1 ring-inset ring-white/10">
            <FolderPlus className="size-4" aria-hidden />
          </span>
          <div className="min-w-0">
            <p className="text-sm font-medium text-foreground">No documents uploaded</p>
            <p className="text-[11px] leading-tight text-muted-foreground">
              Upload documents to let DOCURA understand your information.
            </p>
          </div>
        </div>
        <Button asChild variant="primary" size="sm" className="mt-3 w-full">
          <Link to="/documents">Upload Documents</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className={cn(base, "border-white/12 bg-elevated")}>
      <div className="flex items-center gap-2">
        <span className="flex size-8 items-center justify-center rounded-lg bg-white/[0.06] text-foreground/80 ring-1 ring-inset ring-white/10">
          <FolderCheck className="size-4" aria-hidden />
        </span>
        <div className="min-w-0">
          <p className="text-sm font-medium text-foreground">Documents ready</p>
          <p className="text-[11px] leading-tight text-muted-foreground">
            {documents.length} document{documents.length === 1 ? "" : "s"} available
            {ready < documents.length ? ` · ${ready} processed` : ""}
          </p>
        </div>
      </div>
      <Button asChild variant="outline" size="sm" className="mt-3 w-full">
        <Link to="/documents">View Documents</Link>
      </Button>
    </div>
  );
}
