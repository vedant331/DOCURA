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

const META: Record<Status, StatusMeta> = {
  ready: { label: "Ready", icon: CheckCircle2, tone: "border-emerald-500/40 text-emerald-300" },
  processing: { label: "Processing", icon: Loader2, tone: "border-muted-foreground/40 text-muted-foreground", spin: true },
  queued: { label: "Queued", icon: Clock, tone: "border-muted-foreground/40 text-muted-foreground" },
  complete: { label: "Complete", icon: CheckCircle2, tone: "border-emerald-500/40 text-emerald-300" },
  failed: { label: "Failed", icon: XCircle, tone: "border-destructive/50 text-destructive" },
  review_required: { label: "Review required", icon: FileWarning, tone: "border-amber-500/40 text-amber-300" },
  needs_review: { label: "Needs review", icon: FileWarning, tone: "border-amber-500/40 text-amber-300" },
  action_required: { label: "Action required", icon: UserRoundCog, tone: "border-amber-500/40 text-amber-300" },
  waiting: { label: "Waiting for you", icon: Clock, tone: "border-amber-500/40 text-amber-300" },
  ambiguous: { label: "Ambiguous", icon: GitCompareArrows, tone: "border-amber-500/40 text-amber-300" },
  conflict: { label: "Conflict", icon: GitCompareArrows, tone: "border-orange-500/50 text-orange-300" },
  missing: { label: "Missing", icon: CircleSlash, tone: "border-muted-foreground/40 text-muted-foreground" },
  blocked: { label: "Blocked", icon: Ban, tone: "border-destructive/50 text-destructive" },
  approved: { label: "Approved", icon: ShieldCheck, tone: "border-emerald-500/40 text-emerald-300" },
  denied: { label: "Denied", icon: ShieldQuestion, tone: "border-destructive/50 text-destructive" },
  matched: { label: "Matched", icon: Sparkles, tone: "border-emerald-500/40 text-emerald-300" },
  multiple: { label: "Multiple candidates", icon: GitCompareArrows, tone: "border-amber-500/40 text-amber-300" },
  preparing: { label: "Preparing", icon: Loader2, tone: "border-muted-foreground/40 text-muted-foreground", spin: true },
  quality_loss: { label: "Quality loss", icon: AlertTriangle, tone: "border-orange-500/50 text-orange-300" },
  declaration: { label: "Declaration — your action", icon: UserRoundCog, tone: "border-amber-500/40 text-amber-300" },
  unknown: { label: "Unknown", icon: CircleHelp, tone: "border-muted-foreground/40 text-muted-foreground" },
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
