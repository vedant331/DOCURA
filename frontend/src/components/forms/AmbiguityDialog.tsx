import { useState } from "react";

import type { Candidate } from "@/components/forms/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

// Ambiguity resolution UI (§20, BR-003). Presents every candidate with its source and the
// reason DOCURA could not decide, lets the user pick one OR supply their own value, or
// skip. It NEVER pre-selects a "most likely" candidate.
export function AmbiguityDialog({
  open,
  onOpenChange,
  fieldLabel,
  candidates,
  reason = "Multiple reasonable values were found.",
  onResolve,
  onSkip,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  fieldLabel: string;
  candidates: Candidate[];
  reason?: string;
  onResolve?: (value: string) => void;
  onSkip?: () => void;
}) {
  const [choice, setChoice] = useState<string | null>(null); // no default selection
  const [own, setOwn] = useState("");

  const resolvedValue = own.trim() || choice;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Ambiguous field — {fieldLabel}</DialogTitle>
          <DialogDescription>{reason} Choose the correct value.</DialogDescription>
        </DialogHeader>

        <fieldset className="space-y-2">
          <legend className="sr-only">Candidates for {fieldLabel}</legend>
          {candidates.map((c, i) => (
            <label
              key={`${c.value}-${i}`}
              className="flex cursor-pointer items-start gap-3 border border-border bg-surface/40 px-3 py-2 has-[:checked]:border-mercury"
            >
              <input
                type="radio"
                name="candidate"
                value={c.value}
                checked={choice === c.value && own.trim() === ""}
                onChange={() => {
                  setChoice(c.value);
                  setOwn("");
                }}
                className="mt-1"
              />
              <span className="min-w-0">
                <span className="block text-sm text-foreground">{c.value}</span>
                {c.source ? <span className="font-mono text-[10px] text-muted-foreground">source: {c.source}</span> : null}
              </span>
            </label>
          ))}
        </fieldset>

        <div>
          <label htmlFor="own-value" className="label-system mb-1 block">
            Or enter your own value
          </label>
          <Input
            id="own-value"
            value={own}
            onChange={(e) => {
              setOwn(e.target.value);
              if (e.target.value) setChoice(null);
            }}
            placeholder="Type a value not listed"
          />
        </div>

        <DialogFooter>
          <Button variant="ghost" onClick={() => onSkip?.()}>
            Skip for now
          </Button>
          <Button variant="primary" disabled={!resolvedValue} onClick={() => resolvedValue && onResolve?.(resolvedValue)}>
            Use this value
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
