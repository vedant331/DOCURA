import {
  AlertTriangle,
  Ban,
  CheckCircle2,
  CircleHelp,
  CircleSlash,
  Clock,
  FileWarning,
  GitCompareArrows,
  Loader2,
  ShieldCheck,
  ShieldQuestion,
  Sparkles,
  UserRoundCog,
  XCircle,
  type LucideIcon,
} from "lucide-react";

import { cn } from "@/lib/utils";

// The one status vocabulary for the whole app (§28). Every state carries a label, an
// icon and a visual treatment, so meaning never rests on colour alone (§28/§31). The
// accessible label is spoken text; the icon reinforces it for sighted low-contrast cases.
export type Status =
  | "ready"
  | "processing"
  | "queued"
  | "complete"
  | "failed"
  | "review_required"
  | "needs_review"
  | "action_required"
  | "waiting"
  | "ambiguous"
  | "conflict"
  | "missing"
  | "blocked"
  | "approved"
  | "denied"
  | "matched"
  | "multiple"
  | "preparing"
  | "quality_loss"
  | "declaration"
  | "unknown";

interface StatusMeta {
  label: string;
  icon: LucideIcon;
  tone: string; // border + text colour classes; paired ALWAYS with the icon + label
  spin?: boolean;
}

// Tones use the DOCURA semantic tokens: success (green) / warning (amber) / review (violet) /
// destructive (red) / neutral grey. Meaning never rests on colour alone — every state also
// carries an icon and a label.
const SUCCESS = "border-success/40 text-success";
const WARNING = "border-warning/40 text-warning";
const REVIEW = "border-review/40 text-review";
const DANGER = "border-destructive/50 text-destructive";
const NEUTRAL = "border-muted-foreground/40 text-muted-foreground";

const META: Record<Status, StatusMeta> = {
  ready: { label: "Ready", icon: CheckCircle2, tone: SUCCESS },
  processing: { label: "Processing", icon: Loader2, tone: NEUTRAL, spin: true },
  queued: { label: "Queued", icon: Clock, tone: NEUTRAL },
  complete: { label: "Complete", icon: CheckCircle2, tone: SUCCESS },
  failed: { label: "Failed", icon: XCircle, tone: DANGER },
  review_required: { label: "Review required", icon: FileWarning, tone: REVIEW },
  needs_review: { label: "Needs review", icon: FileWarning, tone: REVIEW },
  action_required: { label: "Action required", icon: UserRoundCog, tone: WARNING },
  waiting: { label: "Waiting for you", icon: Clock, tone: WARNING },
  ambiguous: { label: "Ambiguous", icon: GitCompareArrows, tone: REVIEW },
  conflict: { label: "Conflict", icon: GitCompareArrows, tone: REVIEW },
  missing: { label: "Missing", icon: CircleSlash, tone: DANGER },
  blocked: { label: "Blocked", icon: Ban, tone: DANGER },
  approved: { label: "Approved", icon: ShieldCheck, tone: SUCCESS },
  denied: { label: "Denied", icon: ShieldQuestion, tone: DANGER },
  matched: { label: "Matched", icon: Sparkles, tone: SUCCESS },
  multiple: { label: "Multiple candidates", icon: GitCompareArrows, tone: REVIEW },
  preparing: { label: "Preparing", icon: Loader2, tone: NEUTRAL, spin: true },
  quality_loss: { label: "Quality loss", icon: AlertTriangle, tone: WARNING },
  declaration: { label: "Declaration — your action", icon: UserRoundCog, tone: WARNING },
  unknown: { label: "Unknown", icon: CircleHelp, tone: NEUTRAL },
};

export function StatusBadge({
  status,
  label,
  className,
}: {
  status: Status;
  label?: string;
  className?: string;
}) {
  const meta = META[status];
  const Icon = meta.icon;
  const text = label ?? meta.label;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 border px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.15em]",
        meta.tone,
        className,
      )}
    >
      <Icon className={cn("size-3", meta.spin && "animate-spin")} aria-hidden />
      <span>{text}</span>
    </span>
  );
}

// Map a backend DocumentStatus onto the shared Status vocabulary.
export function documentStatusToStatus(s: string): Status {
  switch (s) {
    case "ready":
      return "ready";
    case "processing":
      return "processing";
    case "queued":
      return "queued";
    case "needs_review":
      return "needs_review";
    case "failed":
      return "failed";
    default:
      return "unknown";
  }
}

// Map a backend FormSessionState onto the shared Status vocabulary.
export function sessionStateToStatus(s: string): Status {
  switch (s) {
    case "active":
      return "ready";
    case "handed_back":
      return "complete";
    case "stopped":
      return "blocked";
    case "expired":
      return "missing";
    default:
      return "unknown";
  }
}
