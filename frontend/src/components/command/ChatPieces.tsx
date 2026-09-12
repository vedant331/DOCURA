import { Sparkles } from "lucide-react";

import { cn } from "@/lib/utils";
import { NotConnected } from "@/components/system/states";

// Small chat building blocks kept together (§6): a suggested prompt chip, a rendered
// message, the assistant not-connected state, and the empty-conversation state.

export function SuggestedPrompt({ text, onSelect }: { text: string; onSelect: (t: string) => void }) {
  return (
    <button
      type="button"
      onClick={() => onSelect(text)}
      className="border border-border bg-surface/40 px-3 py-2 text-left text-xs text-muted-foreground transition-colors hover:border-mercury/40 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      {text}
    </button>
  );
}

export type ChatRole = "user" | "assistant" | "system";
export interface ChatMessageData {
  id: string;
  role: ChatRole;
  text: string;
}

export function ChatMessage({ message }: { message: ChatMessageData }) {
  const mine = message.role === "user";
  const system = message.role === "system";
  return (
    <div className={cn("flex", mine ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[80%] px-3 py-2 text-sm",
          mine
            ? "border border-border bg-surface text-foreground"
            : system
              ? "border border-dashed border-border bg-surface/30 font-mono text-[11px] uppercase tracking-[0.1em] text-muted-foreground"
              : "border border-border bg-surface-2 text-foreground",
        )}
      >
        {message.text}
      </div>
    </div>
  );
}

// Honest assistant state — there is no assistant endpoint yet, so we say so plainly
// rather than faking "AI is thinking" or an answer (§6/§37).
export function AssistantState() {
  return (
    <NotConnected
      title="Assistant not connected"
      description="DOCURA's document assistant is not available yet. When it is connected, it will answer here using only your own documents — nothing is generated in the meantime."
    />
  );
}

export function EmptyConversationState({
  prompts,
  onSelect,
}: {
  prompts: string[];
  onSelect: (t: string) => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-foreground">
        <Sparkles className="size-4 text-mercury" aria-hidden />
        <p className="text-sm font-semibold">How can DOCURA help?</p>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {prompts.map((p) => (
          <SuggestedPrompt key={p} text={p} onSelect={onSelect} />
        ))}
      </div>
    </div>
  );
}
