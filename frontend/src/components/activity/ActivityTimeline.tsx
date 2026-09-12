import { Link } from "react-router-dom";
import {
  CheckCircle2,
  CircleSlash,
  FileUp,
  HandMetal,
  MessageCircleQuestion,
  MousePointerClick,
  Paperclip,
  PenLine,
  Power,
  ShieldCheck,
  XCircle,
  type LucideIcon,
} from "lucide-react";

import type { FormActionResponse, FormActionType, FormActionOutcome } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

// User-viewable audit (§15, FR-AUD-004). Renders recorded form-session actions — never
// editable (FR-AUD-005), never third-party form content (FR-AUD-006). The description is
// built from the action type + DOCURA's own note (detail), not from form data.

const TYPE_META: Record<FormActionType, { label: string; icon: LucideIcon }> = {
  hand_back: { label: "Handed back to user", icon: HandMetal },
  stop: { label: "Session stopped", icon: Power },
  fill: { label: "Field filled", icon: PenLine },
  select: { label: "Option selected", icon: MousePointerClick },
  attach: { label: "Document attached", icon: Paperclip },
  ask: { label: "Question asked", icon: MessageCircleQuestion },
  answer: { label: "Answer recorded", icon: PenLine },
  approval_request: { label: "Approval requested", icon: ShieldCheck },
  approval_decision: { label: "Approval decision", icon: ShieldCheck },
  override: { label: "Value overridden", icon: PenLine },
};

const OUTCOME_ICON: Record<FormActionOutcome, LucideIcon> = {
  succeeded: CheckCircle2,
  failed: XCircle,
  skipped: CircleSlash,
};

export function ActivityItem({ action }: { action: FormActionResponse }) {
  const meta = TYPE_META[action.action_type] ?? { label: action.action_type, icon: FileUp };
  const Icon = meta.icon;
  const OutcomeIcon = OUTCOME_ICON[action.outcome];
  return (
    <li className="flex gap-3 border-b border-border py-4 last:border-b-0">
      <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center border border-border bg-surface/50 text-muted-foreground">
        <Icon className="size-4" aria-hidden />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-sm font-medium text-foreground">{meta.label}</p>
          <span className="inline-flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
            <OutcomeIcon className="size-3" aria-hidden />
            {action.outcome}
          </span>
        </div>
        {action.field_ref ? (
          <p className="mt-0.5 font-mono text-[11px] text-muted-foreground">field: {action.field_ref}</p>
        ) : null}
        {action.detail ? <p className="mt-1 text-sm text-muted-foreground">{action.detail}</p> : null}
        <div className="mt-1 flex flex-wrap items-center gap-3 font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground/70">
          <span>{formatDateTime(action.created_at)}</span>
          {action.document_id ? (
            <Link to={`/app/documents/${action.document_id}`} className="hover:text-foreground">
              related document
            </Link>
          ) : null}
        </div>
      </div>
    </li>
  );
}

export function ActivityTimeline({ actions }: { actions: FormActionResponse[] }) {
  return (
    <ul className="border border-border bg-surface/30 px-4">
      {actions.map((a) => (
        <ActivityItem key={a.id} action={a} />
      ))}
    </ul>
  );
}
