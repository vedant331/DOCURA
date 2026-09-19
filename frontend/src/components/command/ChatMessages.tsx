import { Link } from "react-router-dom";
import {
  AlertTriangle,
  CheckCircle2,
  CircleDashed,
  HelpCircle,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type {
  AssistantBlock,
  ChatMessageData,
  RequirementItem,
  RequirementStatus,
} from "@/components/command/chat-types";

// The DOCURA assistant mark — a monochrome glyph used as the assistant avatar (no colour).
function AssistantAvatar() {
  return (
    <span
      aria-hidden
      className="flex size-8 shrink-0 items-center justify-center rounded-xl bg-white/[0.06] ring-1 ring-inset ring-white/10"
    >
      <Sparkles className="size-4 text-foreground/80" />
    </span>
  );
}

// ---- status chip for requirement rows --------------------------------------------------
// Colour appears ONLY here, and only to communicate meaning (subtle, never neon). The base UI
// stays black/white/grey; "unknown" is neutral grey.
const STATUS: Record<RequirementStatus, { label: string; className: string; Icon: typeof CheckCircle2 }> = {
  available: { label: "Available", className: "bg-emerald-500/10 text-emerald-400 ring-emerald-500/20", Icon: CheckCircle2 },
  needs_approval: { label: "Needs approval", className: "bg-amber-500/10 text-amber-400 ring-amber-500/20", Icon: ShieldCheck },
  needs_review: { label: "Needs review", className: "bg-orange-500/10 text-orange-400 ring-orange-500/20", Icon: HelpCircle },
  missing: { label: "Missing", className: "bg-red-500/10 text-red-400 ring-red-500/20", Icon: CircleDashed },
  unknown: { label: "Unknown", className: "bg-white/5 text-muted-foreground ring-white/10", Icon: HelpCircle },
};

export function StatusChip({ status }: { status: RequirementStatus }) {
  const s = STATUS[status];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium ring-1 ring-inset",
        s.className,
      )}
    >
      <s.Icon className="size-3.5" aria-hidden />
      {s.label}
    </span>
  );
}

function RequirementCard({ item }: { item: RequirementItem }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-white/8 bg-white/[0.02] px-3.5 py-3 transition-colors hover:border-white/15">
      <div className="min-w-0">
        <p className="text-sm font-medium text-foreground">{item.label}</p>
        {item.note ? <p className="mt-0.5 text-xs text-muted-foreground">{item.note}</p> : null}
      </div>
      <StatusChip status={item.status} />
    </div>
  );
}

// ---- one structured assistant block ----------------------------------------------------
function Block({ block }: { block: AssistantBlock }) {
  switch (block.kind) {
    case "heading":
      return <h3 className="text-sm font-semibold tracking-tight text-foreground">{block.text}</h3>;
    case "text":
      return <p className="text-sm leading-relaxed text-muted-foreground">{block.text}</p>;
    case "requirements":
      return (
        <div className="grid gap-2 sm:grid-cols-2">
          {block.items.map((item) => (
            <RequirementCard key={item.label} item={item} />
          ))}
        </div>
      );
    case "warning":
      return (
        <div className="flex items-start gap-2.5 rounded-xl border border-white/10 bg-white/[0.03] px-3.5 py-3">
          <AlertTriangle className="mt-0.5 size-4 shrink-0 text-foreground/60" aria-hidden />
          <p className="text-xs leading-relaxed text-foreground/90">{block.text}</p>
        </div>
      );
    case "approval":
      return (
        <div className="flex items-start gap-2.5 rounded-xl border border-white/10 bg-white/[0.03] px-3.5 py-3">
          <ShieldCheck className="mt-0.5 size-4 shrink-0 text-foreground/60" aria-hidden />
          <p className="text-xs leading-relaxed text-foreground/90">{block.text}</p>
        </div>
      );
    case "actions":
      return (
        <div className="flex flex-wrap gap-2 pt-0.5">
          {block.items.map((a) =>
            a.to ? (
              <Button key={a.label} asChild variant={a.variant ?? "outline"} size="sm">
                <Link to={a.to}>{a.label}</Link>
              </Button>
            ) : (
              <Button key={a.label} variant={a.variant ?? "outline"} size="sm" disabled>
                {a.label}
              </Button>
            ),
          )}
        </div>
      );
    default:
      return null;
  }
}

export function UserMessage({ text }: { text: string }) {
  return (
    <div className="flex animate-message-in justify-end">
      <div className="max-w-[80%] rounded-2xl rounded-br-md border border-white/10 bg-elevated-2 px-4 py-2.5 text-sm leading-relaxed text-foreground shadow-lg shadow-black/30">
        {text}
      </div>
    </div>
  );
}

export function AssistantMessage({ blocks, text }: { blocks?: AssistantBlock[]; text?: string }) {
  return (
    <div className="flex animate-message-in items-start gap-3">
      <AssistantAvatar />
      <div className="min-w-0 flex-1 space-y-3 rounded-2xl rounded-tl-md border border-white/8 bg-surface/70 px-4 py-3.5">
        {text ? <p className="text-sm leading-relaxed text-muted-foreground">{text}</p> : null}
        {blocks?.map((block, i) => <Block key={i} block={block} />)}
      </div>
    </div>
  );
}

export function TypingIndicator() {
  return (
    <div className="flex animate-message-in items-start gap-3">
      <AssistantAvatar />
      <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-md border border-white/8 bg-surface/70 px-4 py-4">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="size-1.5 rounded-full bg-foreground/60 [animation:docura-typing_1.2s_infinite_ease-in-out]"
            style={{ animationDelay: `${i * 0.15}s` }}
            aria-hidden
          />
        ))}
        <span className="sr-only">DOCURA is preparing a response</span>
      </div>
    </div>
  );
}

// Dispatch one message to its presentation.
export function ChatMessage({ message }: { message: ChatMessageData }) {
  if (message.role === "user") return <UserMessage text={message.text ?? ""} />;
  if (message.type === "loading") return <TypingIndicator />;
  return <AssistantMessage blocks={message.blocks} text={message.text} />;
}
