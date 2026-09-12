import { NotConnected } from "@/components/system/states";

// /app/forms/:sessionId/approval — sensitive disclosure approvals (§14/§24). Each approval
// is per-instance: one specific value/document, to one specific field, in one specific
// form — never "approve all", never inherited across fields/forms/sessions. The approval
// request and decision happen in the extension flow (the SensitiveApprovalDialog component
// is the exact UI), and are recorded in the session audit. The web backend does not expose
// a pending-approvals queue, so this screen is an honest seam.
export default function ApprovalPage() {
  return (
    <div className="space-y-4">
      <NotConnected
        title="Approvals happen in the form flow"
        description="When a sensitive value or document needs to be disclosed to a field, DOCURA asks you to approve that one disclosure — showing exactly what, to which field, and why. Approvals are per-instance and never carry to another field, form, or session. These prompts appear in the extension while you're on the form; their decisions are recorded in this session's audit."
      />
      <div className="border border-border bg-surface/30 p-4 text-sm text-muted-foreground">
        <p className="label-system mb-2">How approval works</p>
        <ul className="list-inside list-disc space-y-1">
          <li>One approval authorises exactly one disclosure</li>
          <li>It shows the value/document, the receiving field, and the reason</li>
          <li>It is never inherited by another field, form, or session</li>
          <li>There is no "approve everything" — each is decided on its own</li>
        </ul>
      </div>
    </div>
  );
}
