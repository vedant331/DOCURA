import { useState, type KeyboardEvent } from "react";
import { CornerDownLeft, FileText } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// The command/chat input (§6). Text, submit, disabled state, keyboard submission
// (Enter sends, Shift+Enter newlines), and an optional document-context indicator. It
// only emits the text upward — it never fabricates an answer.
export function ChatComposer({
  onSubmit,
  disabled,
  placeholder = "How can DOCURA help?",
  contextCount,
}: {
  onSubmit: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
  contextCount?: number;
}) {
  const [text, setText] = useState("");

  const send = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setText("");
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className={cn("border border-border bg-surface/60 focus-within:border-mercury/40", disabled && "opacity-60")}>
      <label htmlFor="command-input" className="sr-only">
        Ask DOCURA
      </label>
      <textarea
        id="command-input"
        rows={2}
        value={text}
        disabled={disabled}
        placeholder={placeholder}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        className="w-full resize-none bg-transparent px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none"
      />
      <div className="flex items-center justify-between border-t border-border px-3 py-2">
        <span className="inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
          {typeof contextCount === "number" ? (
            <>
              <FileText className="size-3" aria-hidden />
              {contextCount} document{contextCount === 1 ? "" : "s"} in context
            </>
          ) : (
            "Enter to send · Shift+Enter for newline"
          )}
        </span>
        <Button variant="primary" size="sm" onClick={send} disabled={disabled || text.trim().length === 0}>
          Send <CornerDownLeft className="size-3.5" aria-hidden />
        </Button>
      </div>
    </div>
  );
}
