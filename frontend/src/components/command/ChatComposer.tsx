import { useRef, useState, type KeyboardEvent } from "react";
import { ArrowUp, Loader2, Mic, Paperclip, FileText } from "lucide-react";

import { cn } from "@/lib/utils";

// The premium chat composer. Text + attachment/document/mic affordances + send button, with
// Enter-to-send / Shift+Enter-for-newline, disabled + loading states, and an honest helper
// line. It only emits the text upward — it never fabricates an answer.
export function ChatComposer({
  onSubmit,
  disabled,
  loading,
  placeholder = "Ask DOCURA anything...",
}: {
  onSubmit: (text: string) => void;
  disabled?: boolean;
  loading?: boolean;
  placeholder?: string;
}) {
  const [text, setText] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);
  const blocked = disabled || loading;

  const grow = () => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  };

  const send = () => {
    const trimmed = text.trim();
    if (!trimmed || blocked) return;
    onSubmit(trimmed);
    setText("");
    requestAnimationFrame(() => {
      if (ref.current) ref.current.style.height = "auto";
    });
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  // Decorative-only affordances (attach / document / mic). They are disabled until wired to a
  // real capability — shown so the composer reads like a real assistant, never faking action.
  const IconBtn = ({ Icon, label }: { Icon: typeof Paperclip; label: string }) => (
    <button
      type="button"
      title={`${label} (coming soon)`}
      aria-label={`${label} (coming soon)`}
      disabled
      className="flex size-8 items-center justify-center rounded-lg text-muted-foreground/70 transition-colors hover:text-foreground disabled:opacity-50"
    >
      <Icon className="size-4" aria-hidden />
    </button>
  );

  return (
    <div className="space-y-2">
      <div
        className={cn(
          "rounded-2xl border border-white/12 bg-elevated shadow-lg shadow-black/30 transition-colors",
          "focus-within:border-white/30",
          blocked && "opacity-60",
        )}
      >
        <label htmlFor="docura-composer" className="sr-only">
          Ask DOCURA
        </label>
        <textarea
          id="docura-composer"
          ref={ref}
          rows={1}
          value={text}
          disabled={blocked}
          placeholder={placeholder}
          onChange={(e) => {
            setText(e.target.value);
            grow();
          }}
          onKeyDown={onKeyDown}
          className="chat-scroll block max-h-[200px] w-full resize-none bg-transparent px-4 pt-3.5 text-[15px] leading-relaxed text-foreground placeholder:text-muted-foreground/60 focus:outline-none"
        />
        <div className="flex items-center justify-between px-2.5 pb-2.5 pt-1">
          <div className="flex items-center gap-0.5">
            <IconBtn Icon={Paperclip} label="Attach a file" />
            <IconBtn Icon={FileText} label="Reference a document" />
            <IconBtn Icon={Mic} label="Voice input" />
          </div>
          <button
            type="button"
            onClick={send}
            disabled={blocked || text.trim().length === 0}
            aria-label="Send message"
            className={cn(
              "flex size-9 items-center justify-center rounded-xl transition-all duration-200",
              "bg-accent text-accent-foreground shadow-md shadow-black/30",
              "hover:bg-accent-hover active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/60",
              "disabled:cursor-not-allowed disabled:bg-accent/15 disabled:text-muted-foreground disabled:shadow-none",
            )}
          >
            {loading ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <ArrowUp className="size-4" aria-hidden />}
          </button>
        </div>
      </div>
      <p className="px-1 text-center text-[11px] text-muted-foreground/70">
        DOCURA only uses information you authorize. Enter to send · Shift+Enter for a new line.
      </p>
    </div>
  );
}
