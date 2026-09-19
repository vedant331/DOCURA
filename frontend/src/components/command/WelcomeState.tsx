import { FileSearch, ClipboardCheck, PenLine, FolderCheck, Sparkles, type LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

// Centered welcome shown when a conversation is empty. No fake conversation is rendered —
// just an honest, premium entry point with useful suggested actions.

export interface Suggestion {
  label: string;
  hint: string;
  prompt: string;
  Icon: LucideIcon;
}

export const SUGGESTIONS: Suggestion[] = [
  {
    label: "Find required documents",
    hint: "See what a typical application needs and what you already have.",
    prompt: "What documents do I need, and which do I already have?",
    Icon: FileSearch,
  },
  {
    label: "Check my application",
    hint: "Review which of your details are ready, missing, or need approval.",
    prompt: "Which of my details are ready, missing, or need review?",
    Icon: ClipboardCheck,
  },
  {
    label: "Fill a form",
    hint: "Learn how DOCURA fills forms safely with your record.",
    prompt: "How does DOCURA fill a form using my documents?",
    Icon: PenLine,
  },
  {
    label: "Review my documents",
    hint: "Summarise what DOCURA has read from your documents.",
    prompt: "Summarise what DOCURA has read from my documents.",
    Icon: FolderCheck,
  },
];

function greeting(now = new Date()): string {
  const h = now.getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

function SuggestionCard({ s, onSelect }: { s: Suggestion; onSelect: (prompt: string) => void }) {
  return (
    <button
      type="button"
      onClick={() => onSelect(s.prompt)}
      className={cn(
        "group flex items-start gap-3 rounded-2xl border border-white/8 bg-white/[0.02] p-4 text-left",
        "transition-all duration-300 hover:-translate-y-0.5 hover:border-white/20 hover:bg-white/[0.05]",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/30",
      )}
    >
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-white/5 text-foreground/70 ring-1 ring-inset ring-white/10 transition-colors group-hover:bg-white/10 group-hover:text-foreground">
        <s.Icon className="size-5" aria-hidden />
      </span>
      <span className="min-w-0">
        <span className="block text-sm font-medium text-foreground">{s.label}</span>
        <span className="mt-0.5 block text-xs leading-relaxed text-muted-foreground">{s.hint}</span>
      </span>
    </button>
  );
}

export function WelcomeState({ onSelect }: { onSelect: (prompt: string) => void }) {
  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col items-center px-2 py-10 text-center animate-fade-in">
      <div className="chat-aura pointer-events-none absolute inset-x-0 top-0 h-64" aria-hidden />
      <span className="mb-5 flex size-12 items-center justify-center rounded-2xl bg-white/[0.06] ring-1 ring-inset ring-white/10">
        <Sparkles className="size-6 text-foreground/80" aria-hidden />
      </span>
      <h2 className="text-2xl font-semibold tracking-tight text-foreground sm:text-[1.75rem]">
        {greeting()} <span aria-hidden>👋</span>
      </h2>
      <p className="mt-2 text-lg font-medium text-foreground/90">How can DOCURA help you today?</p>
      <p className="mt-2 max-w-md text-sm leading-relaxed text-muted-foreground">
        Ask about your documents, forms, applications, or tasks. DOCURA answers using only the
        information you authorize.
      </p>

      <div className="mt-8 grid w-full gap-3 sm:grid-cols-2">
        {SUGGESTIONS.map((s) => (
          <SuggestionCard key={s.label} s={s} onSelect={onSelect} />
        ))}
      </div>
    </div>
  );
}
