import type { ReadinessData } from "@/components/forms/types";
import { FieldList } from "@/components/forms/FieldList";

// Readiness screen body (§18). Shows what the form needs vs what is available/missing and
// what requires the user, then the per-field breakdown. Renders only supplied data.
export function ReadinessSummary({ data }: { data: ReadinessData }) {
  const cells = [
    { k: "Required fields", v: data.requiredFields },
    { k: "Required documents", v: data.requiredDocuments },
    { k: "Available", v: data.available },
    { k: "Missing", v: data.missing },
    { k: "Needs you", v: data.requiresUser },
  ];
  return (
    <div className="space-y-6">
      <div className="grid gap-px overflow-hidden border border-border bg-border sm:grid-cols-5">
        {cells.map((c) => (
          <div key={c.k} className="bg-surface/50 p-4">
            <p className="label-system">{c.k}</p>
            <p className="mt-1 text-xl font-bold text-foreground">{c.v}</p>
          </div>
        ))}
      </div>
      <FieldList fields={data.fields} />
    </div>
  );
}
