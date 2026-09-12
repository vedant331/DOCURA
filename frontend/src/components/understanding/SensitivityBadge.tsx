import { Eye, EyeOff, ShieldAlert } from "lucide-react";
import { useState } from "react";

import { cn } from "@/lib/utils";

// The three-tier sensitivity vocabulary (FR-INF-007). Tier ASSIGNMENT is blocked on
// G-14/A-5, so no attribute currently carries a real tier — the honest default is
// `unclassified`, shown plainly rather than guessed as routine or sensitive.
export type SensitivityTier = "routine" | "sensitive" | "consequential" | "unclassified";

const META: Record<SensitivityTier, { label: string; tone: string }> = {
  routine: { label: "Routine", tone: "border-border text-muted-foreground" },
  sensitive: { label: "Sensitive", tone: "border-amber-500/40 text-amber-300" },
  consequential: { label: "Consequential", tone: "border-orange-500/50 text-orange-300" },
  unclassified: { label: "Unclassified", tone: "border-border text-muted-foreground" },
};

export function SensitivityBadge({
  tier = "unclassified",
  className,
}: {
  tier?: SensitivityTier;
  className?: string;
}) {
  const meta = META[tier];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 border px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.15em]",
        meta.tone,
        className,
      )}
    >
      <ShieldAlert className="size-2.5" aria-hidden />
      {meta.label}
    </span>
  );
}

// A value that is masked by default when its tier is sensitive/consequential (FR-SENS-004),
// revealed only on explicit user action. Routine/unclassified values are shown directly.
export function SensitiveValue({
  value,
  tier = "unclassified",
}: {
  value: string;
  tier?: SensitivityTier;
}) {
  const mustMask = tier === "sensitive" || tier === "consequential";
  const [revealed, setRevealed] = useState(false);
  if (!mustMask) return <span className="text-foreground">{value}</span>;
  return (
    <span className="inline-flex items-center gap-2">
      <span className="font-mono text-foreground">{revealed ? value : "•".repeat(Math.min(value.length, 12))}</span>
      <button
        type="button"
        onClick={() => setRevealed((r) => !r)}
        className="text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        aria-label={revealed ? "Hide value" : "Reveal value"}
      >
        {revealed ? <EyeOff className="size-3.5" aria-hidden /> : <Eye className="size-3.5" aria-hidden />}
      </button>
    </span>
  );
}
