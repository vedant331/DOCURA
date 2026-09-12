import { useEffect, useState } from "react";
import { Download, ZoomIn, ZoomOut } from "lucide-react";

import * as api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ErrorState, LoadingState } from "@/components/system/states";

// Renders the ORIGINAL file exactly as uploaded (FR-DOC-004). Fetches the bytes as an
// authenticated blob and shows an <img> (images, with zoom) or an <iframe> (PDF — the
// browser viewer handles page navigation for multi-page documents, FR-OCR-008). The blob
// URL is revoked on unmount. Nothing here modifies the stored original.
export function DocumentPreview({
  documentId,
  contentType,
  filename,
}: {
  documentId: string;
  contentType: string;
  filename: string;
}) {
  const [url, setUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    let objectUrl: string | null = null;
    let cancelled = false;
    setError(null);
    setUrl(null);
    api
      .downloadDocument(documentId)
      .then((blob) => {
        if (cancelled) return;
        objectUrl = URL.createObjectURL(blob);
        setUrl(objectUrl);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof api.ApiError ? e.message : "Could not load the document.");
      });
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [documentId]);

  const isImage = contentType.startsWith("image/");
  const isPdf = contentType === "application/pdf";

  return (
    <div className="flex flex-col">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <span className="font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">Original</span>
        <div className="flex items-center gap-1">
          {isImage ? (
            <>
              <Button variant="ghost" size="icon" aria-label="Zoom out" onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))}>
                <ZoomOut className="size-4" aria-hidden />
              </Button>
              <Button variant="ghost" size="icon" aria-label="Zoom in" onClick={() => setZoom((z) => Math.min(3, z + 0.25))}>
                <ZoomIn className="size-4" aria-hidden />
              </Button>
            </>
          ) : null}
          {url ? (
            <Button asChild variant="ghost" size="sm">
              <a href={url} download={filename}>
                <Download className="size-3.5" aria-hidden /> Download
              </a>
            </Button>
          ) : null}
        </div>
      </div>

      <div className="min-h-[24rem] bg-bg">
        {error ? (
          <ErrorState message={error} />
        ) : !url ? (
          <LoadingState label="Loading document" />
        ) : isImage ? (
          <div className="max-h-[70vh] overflow-auto p-4 text-center">
            <img
              src={url}
              alt={`Preview of ${filename}`}
              style={{ transform: `scale(${zoom})`, transformOrigin: "top center" }}
              className="mx-auto max-w-full transition-transform"
            />
          </div>
        ) : isPdf ? (
          <iframe title={`Preview of ${filename}`} src={url} className="h-[70vh] w-full" />
        ) : (
          <div className="p-8 text-center">
            <p className="text-sm text-muted-foreground">
              Preview is not available for this file type ({contentType}).
            </p>
            <Button asChild variant="outline" size="sm" className="mt-4">
              <a href={url} download={filename}>
                <Download className="size-3.5" aria-hidden /> Download original
              </a>
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
