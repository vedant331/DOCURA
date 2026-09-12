import { HandMetal, ShieldCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/system/StatusBadge";

// Hand-back state (§27, BR-008). DOCURA never submits and never operates a submit control;
// this panel states that plainly and offers only to hand control back to the user. There
// is deliberately no "Submit form" action here.
export function HandBackPanel({
  outstandingCount,
  handedBack,
  onHandBack,
  handingBack,
}: {
  // `null` means the blocker count is not known on the web side (field-level state lives
  // in the extension and is not bridged) — shown as an honest "unknown" rather than "0".
  outstandingCount: number | null;
  handedBack: boolean;
  onHandBack?: () => void;
  handingBack?: boolean;
}) {
  const ready = outstandingCount === 0;
  return (
    <section className="border border-border bg-surface/40 p-6">
      <div className="flex items-center gap-2">
        <HandMetal className="size-5 text-mercury" aria-hidden />
        <h3 className="text-lg font-bold text-foreground">
          {handedBack ? "Handed back to you" : "DOCURA is ready for your review"}
        </h3>
      </div>

      <div className="mt-3">
        {outstandingCount === null ? (
          <StatusBadge status="unknown" label="Blockers tracked in session" />
        ) : ready ? (
          <StatusBadge status="complete" label="No blockers" />
        ) : (
          <StatusBadge status="action_required" label={`${outstandingCount} outstanding`} />
        )}
      </div>

      <p className="mt-4 max-w-prose text-sm leading-relaxed text-muted-foreground">
        DOCURA does not submit the form. When you are ready, submission is yours to perform in the
        form itself — DOCURA hands control back and never operates the submit control.
      </p>

      <div className="mt-5 flex flex-wrap items-center gap-2">
        {!handedBack ? (
          <Button variant="primary" onClick={onHandBack} loading={handingBack} loadingLabel="Handing back">
            Hand back to me
          </Button>
        ) : (
          <p className="inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-[0.15em] text-emerald-300">
            <ShieldCheck className="size-3.5" aria-hidden />
            Control is yours — submit the form yourself.
          </p>
        )}
      </div>
    </section>
  );
}
