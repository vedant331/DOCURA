import { ShieldAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { SensitiveValue } from "@/components/understanding/SensitivityBadge";

// Per-instance sensitive disclosure approval (§14/§24, BR-005/BR-007). Shows exactly WHAT
// will be disclosed, TO WHICH field/form, and WHY. Approval is for THIS one disclosure
// only — the copy is explicit that it does not carry to any other field, form, or session,
// and there is no "approve all" control.
export function SensitiveApprovalDialog({
  open,
  onOpenChange,
  what,
  isDocument = false,
  targetField,
  targetForm,
  reason,
  onDecision,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  what: string;
  isDocument?: boolean;
  targetField: string;
  targetForm: string;
  reason: string;
  onDecision?: (approved: boolean) => void;
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShieldAlert className="size-5 text-amber-300" aria-hidden />
            Approve this disclosure
          </DialogTitle>
          <DialogDescription>
            This approval covers only this one disclosure. It does not carry to any other field, form,
            or session.
          </DialogDescription>
        </DialogHeader>

        <dl className="space-y-3 border border-border bg-surface/40 p-4 text-sm">
          <div>
            <dt className="label-system">{isDocument ? "Document to disclose" : "Value to disclose"}</dt>
            <dd className="mt-1">
              {isDocument ? <span className="text-foreground">{what}</span> : <SensitiveValue value={what} tier="sensitive" />}
            </dd>
          </div>
          <div>
            <dt className="label-system">Receiving field</dt>
            <dd className="mt-1 font-mono text-foreground">{targetField}</dd>
          </div>
          <div>
            <dt className="label-system">Form / session</dt>
            <dd className="mt-1 font-mono text-foreground">{targetForm}</dd>
          </div>
          <div>
            <dt className="label-system">Why</dt>
            <dd className="mt-1 text-muted-foreground">{reason}</dd>
          </div>
        </dl>

        <DialogFooter>
          <Button variant="ghost" onClick={() => onDecision?.(false)}>
            Deny
          </Button>
          <Button variant="primary" onClick={() => onDecision?.(true)}>
            Approve this disclosure
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
