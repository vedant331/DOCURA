import { NotConnected } from "@/components/system/states";

// /app/forms/:sessionId/readiness — what the form needs before continuing (§18). Readiness
// (required fields/documents, what's available, what's missing, what needs the user) is
// computed by the extension's readiness module in its isolated world. The web backend
// stores only session lifecycle + audit, so this data is not available here. Rather than
// fabricate counts, the web app states this plainly. The ReadinessSummary / FieldList
// components are the ready-to-use seam a future extension→web bridge would populate.
export default function ReadinessPage() {
  return (
    <div className="space-y-4">
      <NotConnected
        title="Readiness is computed in the extension"
        description="Required fields and documents, what your record can supply, what's missing, and what needs your input are determined inside the browser extension while you're on the form. They are not sent to the web backend, so the web app cannot display per-field readiness here."
      />
      <div className="border border-border bg-surface/30 p-4 text-sm text-muted-foreground">
        <p className="label-system mb-2">What this screen will show</p>
        <ul className="list-inside list-disc space-y-1">
          <li>Required fields and required documents for the form</li>
          <li>Information your record can supply, and what is missing</li>
          <li>Fields that need your input, and any blockers</li>
        </ul>
      </div>
    </div>
  );
}
