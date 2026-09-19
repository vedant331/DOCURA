import { useState } from "react";
import { useMemo } from "react";
import { Download } from "lucide-react";

import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";
import { useAsync } from "@/hooks/useAsync";
import { attributeGroup } from "@/lib/format";
import { PageHeader } from "@/components/app/PageHeader";
import { Button } from "@/components/ui/button";
import { RecordSection } from "@/components/record/RecordSection";
import { EmptyState, ErrorState, LoadingState, NotConnected } from "@/components/system/states";

// /app/record — the user's structured record (§13). Attributes assembled from their
// documents, grouped by scope, each with value/source/confidence/sensitivity and a
// conflict indicator. Only attributes the backend actually returns are shown — nothing is
// invented. Empty until extraction has produced observations (OCR engine unconfigured).
export default function MyRecordPage() {
  const record = useAsync(() => api.getRecord());
  const docs = useAsync(() => api.listDocuments());
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // Export the complete record (FR-ACC-006). Fetch the JSON as a Blob and offer it as a
  // download; nothing is modified server-side.
  const exportRecord = async () => {
    setExporting(true);
    setExportError(null);
    try {
      const blob = await api.exportRecord();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "docura-record-export.json";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setExportError(err instanceof ApiError ? err.message : "Could not export your record.");
    } finally {
      setExporting(false);
    }
  };

  const docNameById = useMemo(() => {
    const map: Record<string, string> = {};
    for (const d of docs.data?.documents ?? []) map[d.id] = d.original_filename;
    return map;
  }, [docs.data]);

  const grouped = useMemo(() => {
    const map = new Map<string, typeof attributes>();
    const attributes = record.data?.attributes ?? [];
    for (const a of attributes) {
      const g = attributeGroup(a.canonical_identifier);
      if (!map.has(g)) map.set(g, []);
      map.get(g)!.push(a);
    }
    return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
  }, [record.data]);

  return (
    <>
      <PageHeader
        eyebrow="My Record"
        title="Your record"
        description="The structured information DOCURA has assembled from your documents, with its source and confidence. You decide any conflicts — DOCURA never picks for you."
        actions={
          <Button variant="outline" onClick={exportRecord} loading={exporting} loadingLabel="Exporting">
            <Download className="size-4" aria-hidden /> Export
          </Button>
        }
      />
      {exportError ? (
        <p role="alert" className="mb-4 border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-foreground">
          {exportError}
        </p>
      ) : null}

      {record.status === "loading" ? (
        <LoadingState label="Assembling your record" />
      ) : record.status === "error" ? (
        <ErrorState message={record.error ?? undefined} onRetry={record.reload} />
      ) : grouped.length === 0 ? (
        <EmptyState
          title="No record data yet"
          description="Your record fills in as DOCURA reads your documents. Upload documents, or wait for processing to finish."
        />
      ) : (
        <div className="space-y-6">
          {grouped.map(([group, attrs]) => (
            <RecordSection key={group} title={group} attributes={attrs} docNameById={docNameById} />
          ))}
          <NotConnected
            title="Sensitivity tiers & corrections"
            description="Sensitivity classification and saving corrections are defined in the UI but their behaviour is a pending product decision (how a correction interacts with future re-extraction, and how conflicts are resolved), so values show as unclassified and corrections are not yet persisted. Conflicts are surfaced here and never auto-resolved."
          />
        </div>
      )}
    </>
  );
}
