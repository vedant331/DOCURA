import { Gavel } from "lucide-react";

import { StatusBadge } from "@/components/system/StatusBadge";

// Declaration / consent control treatment (§25, BR-006). DOCURA never ticks or accepts a
// declaration — the UI states plainly that the user must decide, and never shows it as
// checked/handled by DOCURA.
export function DeclarationWarning({ fieldLabel }: { fieldLabel: string }) {
  return (
    <div className="flex items-start gap-3 border border-amber-500/40 bg-amber-500/5 px-3 py-3">
      <Gavel className="mt-0.5 size-4 shrink-0 text-amber-300" aria-hidden />
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status="declaration" label="Declaration — you must decide" />
        </div>
        <p className="mt-1 text-sm text-foreground">{fieldLabel}</p>
        <p className="mt-1 text-sm text-muted-foreground">
          DOCURA will never accept, tick, or complete this on your behalf. You must review and act
          on it yourself.
        </p>
      </div>
    </div>
  );
}
