import { useMemo, useState } from "react";
import { CheckCircle2, FileText, Loader2, X, XCircle } from "lucide-react";

import * as api from "@/lib/api";
import type { UploadLimits, UploadResponse } from "@/lib/api";
import { formatBytes } from "@/lib/format";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { UploadDropzone } from "@/components/documents/UploadDropzone";
import { ErrorState } from "@/components/system/states";

// The complete upload experience (§8): idle → selected → uploading → completed/failed.
// Client-side validation mirrors the backend's stated limits (FR-UPL-003) so obviously
// invalid files are caught before the request; the backend remains the authority and its
// per-file rejections are shown too. Real POST /documents — no fabricated completion.

type Phase = "idle" | "uploading" | "done" | "error";

interface QueuedFile {
  file: File;
  invalidReason?: string;
}

function validate(file: File, limits: UploadLimits | null): string | undefined {
  if (!limits) return undefined;
  const name = file.name.toLowerCase();
  const extOk = limits.accepted_extensions.some((ext) => name.endsWith(ext.toLowerCase()));
  if (!extOk) return `Unsupported type. Accepted: ${limits.accepted_extensions.join(", ")}`;
  if (file.size > limits.max_document_bytes)
    return `Too large (${formatBytes(file.size)}). Max ${formatBytes(limits.max_document_bytes)}.`;
  return undefined;
}

export function UploadDialog({
  open,
  onOpenChange,
  limits,
  onUploaded,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  limits: UploadLimits | null;
  onUploaded?: () => void;
}) {
  const [queue, setQueue] = useState<QueuedFile[]>([]);
  const [phase, setPhase] = useState<Phase>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadResponse | null>(null);

  const accept = limits?.accepted_extensions.join(",");
  const maxCount = limits?.max_documents_per_upload ?? 5;
  const validFiles = useMemo(() => queue.filter((q) => !q.invalidReason), [queue]);

  const reset = () => {
    setQueue([]);
    setPhase("idle");
    setError(null);
    setResult(null);
  };

  const addFiles = (files: File[]) => {
    setPhase("idle");
    setResult(null);
    setError(null);
    setQueue((prev) => {
      const merged = [...prev, ...files.map((file) => ({ file, invalidReason: validate(file, limits) }))];
      return merged.slice(0, maxCount + prev.length); // soft cap; backend enforces the real one
    });
  };

  const removeAt = (i: number) => setQueue((q) => q.filter((_, idx) => idx !== i));

  const doUpload = async () => {
    if (validFiles.length === 0) return;
    setPhase("uploading");
    setError(null);
    try {
      const res = await api.uploadDocuments(validFiles.map((q) => q.file));
      setResult(res);
      setPhase("done");
      onUploaded?.();
    } catch (e) {
      setError(e instanceof api.ApiError ? e.message : "Upload failed.");
      setPhase("error");
    }
  };

  const close = (o: boolean) => {
    if (phase === "uploading") return; // don't close mid-upload
    if (!o) reset();
    onOpenChange(o);
  };

  return (
    <Dialog open={open} onOpenChange={close}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Upload documents</DialogTitle>
          <DialogDescription>
            {limits
              ? `PDF, JPG or PNG · up to ${formatBytes(limits.max_document_bytes)} each · up to ${limits.max_documents_per_upload} at a time.`
              : "Add PDF, JPG or PNG files to your vault."}
          </DialogDescription>
        </DialogHeader>

        {phase === "done" && result ? (
          <div className="space-y-3" role="status">
            <div className="flex items-center gap-2 border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">
              <CheckCircle2 className="size-4" aria-hidden />
              {result.accepted.length} document{result.accepted.length === 1 ? "" : "s"} added and queued for processing.
            </div>
            {result.rejected.length > 0 ? (
              <ul className="space-y-1">
                {result.rejected.map((r, i) => (
                  <li key={i} className="flex items-start gap-2 border border-destructive/40 bg-destructive/10 px-3 py-2 text-xs text-destructive">
                    <XCircle className="mt-0.5 size-3.5 shrink-0" aria-hidden />
                    <span><strong>{r.filename}</strong> — {r.reason}. {r.remediation}</span>
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
        ) : (
          <>
            <UploadDropzone onFiles={addFiles} accept={accept} disabled={phase === "uploading"} />

            {queue.length > 0 ? (
              <ul className="max-h-52 space-y-1.5 overflow-y-auto" aria-label="Selected files">
                {queue.map((q, i) => (
                  <li
                    key={`${q.file.name}-${i}`}
                    className="flex items-center gap-3 border border-border bg-surface/40 px-3 py-2"
                  >
                    <FileText className="size-4 shrink-0 text-muted-foreground" aria-hidden />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm text-foreground">{q.file.name}</p>
                      <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
                        {formatBytes(q.file.size)}
                      </p>
                      {q.invalidReason ? (
                        <p className="mt-0.5 font-mono text-[10px] text-destructive">{q.invalidReason}</p>
                      ) : null}
                    </div>
                    {phase === "uploading" ? (
                      <Loader2 className="size-4 animate-spin text-muted-foreground" aria-hidden />
                    ) : (
                      <button
                        type="button"
                        onClick={() => removeAt(i)}
                        className="text-muted-foreground hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                        aria-label={`Remove ${q.file.name}`}
                      >
                        <X className="size-4" aria-hidden />
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            ) : null}

            {phase === "error" && error ? <ErrorState message={error} onRetry={doUpload} /> : null}
          </>
        )}

        <DialogFooter>
          {phase === "done" ? (
            <>
              <Button variant="ghost" onClick={reset}>Add more</Button>
              <Button variant="primary" onClick={() => close(false)}>Done</Button>
            </>
          ) : (
            <>
              <Button variant="ghost" onClick={() => close(false)} disabled={phase === "uploading"}>
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={doUpload}
                disabled={validFiles.length === 0}
                loading={phase === "uploading"}
                loadingLabel="Uploading"
              >
                Upload {validFiles.length > 0 ? `(${validFiles.length})` : ""}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
