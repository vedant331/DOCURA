import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { NotConnected } from "@/components/system/states";
import { attributeLabel } from "@/lib/format";

// Correction UI for an extracted value (§11). A user-supplied value would become
// authoritative over the extracted one (FR-INF-003, BR-012) and be clearly marked
// "USER CORRECTED". The backend record API is currently READ-ONLY (no write endpoint),
// so Save is an honest seam: the form is complete and validated, but persistence is
// disabled and labelled rather than faked.
export function CorrectionDialog({
  open,
  onOpenChange,
  canonicalIdentifier,
  currentValue,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  canonicalIdentifier: string;
  currentValue: string | null;
}) {
  const [draft, setDraft] = useState(currentValue ?? "");
  const label = attributeLabel(canonicalIdentifier);
  const invalid = draft.trim().length === 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Correct {label}</DialogTitle>
          <DialogDescription>
            A value you enter becomes authoritative over what DOCURA extracted, and is kept even if
            the document is reprocessed.
          </DialogDescription>
        </DialogHeader>

        <div>
          <Label htmlFor="correction-input" className="mb-2">
            Corrected value
          </Label>
          <Input
            id="correction-input"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            aria-invalid={invalid || undefined}
            autoFocus
          />
          {invalid ? (
            <p className="mt-2 font-mono text-[11px] text-destructive">A value is required.</p>
          ) : (
            <p className="mt-2 inline-flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.15em] text-emerald-300">
              User corrected value
            </p>
          )}
        </div>

        <NotConnected
          title="Saving not yet connected"
          description="Persisting a correction needs a record write endpoint that does not exist yet. Your input is validated here but not stored."
        />

        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button variant="primary" disabled title="Correction persistence is not yet available">
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
