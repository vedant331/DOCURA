import { useMemo } from "react";

import * as api from "@/lib/api";
import { useAsync } from "@/hooks/useAsync";
import { attributeGroup } from "@/lib/format";
import { PageHeader } from "@/components/app/PageHeader";
import { RecordSection } from "@/components/record/RecordSection";
import { EmptyState, ErrorState, LoadingState, NotConnected } from "@/components/system/states";

// /app/record — the user's structured record (§13). Attributes assembled from their
// documents, grouped by scope, each with value/source/confidence/sensitivity and a
// conflict indicator. Only attributes the backend actually returns are shown — nothing is
// invented. Empty until extraction has produced observations (OCR engine unconfigured).
export default function MyRecordPage() {
  const record = useAsync(() => api.getRecord());
  const docs = useAsync(() => api.listDocuments());

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
      />

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
            description="Sensitivity classification and saving corrections are defined in the UI but need backend capabilities that are not available yet, so values show as unclassified and corrections are not persisted."
          />
        </div>
      )}
    </>
  );
}
