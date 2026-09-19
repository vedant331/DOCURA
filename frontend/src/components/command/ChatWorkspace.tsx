import { useCallback, useEffect, useRef, useState } from "react";
import { Plus } from "lucide-react";

import * as api from "@/lib/api";
import { ApiError, type DocumentResponse } from "@/lib/api";
import { useAuth } from "@/auth/AuthContext";
import { Button } from "@/components/ui/button";
import { ChatComposer } from "@/components/command/ChatComposer";
import { ChatMessage, TypingIndicator } from "@/components/command/ChatMessages";
import { DocumentStatusCard } from "@/components/command/DocumentStatusCard";
import { WelcomeState } from "@/components/command/WelcomeState";
import {
  toAssistantMessage,
  toChatMessage,
  userMessage,
  type ChatMessageData,
} from "@/components/command/chat-types";

// The primary chat workspace (§5/§6). The backend is the source of truth: on mount it restores
// the most recent conversation (or creates one), and every reply comes from
// POST /conversations/{id}/messages — there is no local/fake AI. Full height: a slim header
// (live document status + New chat), a scrolling message stream, and a sticky composer.
export function ChatWorkspace({
  documents,
  documentsLoading,
}: {
  documents: DocumentResponse[] | null;
  documentsLoading?: boolean;
}) {
  const { signOut } = useAuth();
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [initializing, setInitializing] = useState(true);
  const [initError, setInitError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [initNonce, setInitNonce] = useState(0);
  const streamRef = useRef<HTMLDivElement>(null);
  const lastText = useRef<string>("");

  // A rejected token means the session ended — return to sign-in (fail toward inaction).
  const handleAuthExpiry = useCallback(
    (err: unknown) => {
      if (err instanceof ApiError && err.status === 401) void signOut();
    },
    [signOut],
  );

  // Restore the most recent conversation (backend-ordered newest-first) or create one.
  useEffect(() => {
    let cancelled = false;
    setInitializing(true);
    setInitError(null);
    (async () => {
      try {
        const list = await api.listConversations();
        const existing = list.conversations[0];
        if (existing) {
          const history = await api.listMessages(existing.id);
          if (cancelled) return;
          setConversationId(existing.id);
          setMessages(history.messages.map(toChatMessage));
        } else {
          const created = await api.createConversation();
          if (cancelled) return;
          setConversationId(created.id);
          setMessages([]);
        }
      } catch (err) {
        if (cancelled) return;
        handleAuthExpiry(err);
        // Non-blocking: the composer stays usable and the first send lazily creates a
        // conversation. A refresh (or Retry) re-attempts restoring history.
        setConversationId(null);
        setInitError(
          err instanceof ApiError ? err.message : "Couldn't load your conversation.",
        );
      } finally {
        if (!cancelled) setInitializing(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [initNonce, handleAuthExpiry]);

  useEffect(() => {
    const el = streamRef.current;
    el?.scrollTo?.({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, pending]);

  // Send a message through the backend. `echo` adds the optimistic user bubble; a retry of a
  // failed send reuses the bubble already on screen and passes echo=false.
  const send = useCallback(
    async (text: string, echo = true) => {
      if (pending) return;
      setSendError(null);
      lastText.current = text;
      if (echo) setMessages((prev) => [...prev, userMessage(text)]);
      setPending(true);
      try {
        let id = conversationId;
        if (!id) {
          const created = await api.createConversation();
          id = created.id;
          setConversationId(id);
        }
        const turn = await api.sendMessage(id, text);
        setMessages((prev) => [...prev, toAssistantMessage(turn.assistant_message)]);
      } catch (err) {
        handleAuthExpiry(err);
        setSendError(
          err instanceof ApiError ? err.message : "Couldn't send your message. Try again.",
        );
      } finally {
        setPending(false);
      }
    },
    [conversationId, pending, handleAuthExpiry],
  );

  const newChat = useCallback(async () => {
    if (pending) return;
    setSendError(null);
    setInitError(null);
    try {
      const created = await api.createConversation();
      setConversationId(created.id);
      setMessages([]);
    } catch (err) {
      handleAuthExpiry(err);
      setSendError(err instanceof ApiError ? err.message : "Couldn't start a new chat.");
    }
  }, [pending, handleAuthExpiry]);

  const empty = messages.length === 0 && !pending;

  return (
    <div className="flex h-full flex-col">
      {/* Workspace header — identity + live document status + New chat. */}
      <header className="flex items-center justify-between gap-4 border-b border-white/8 px-4 py-3 sm:px-6">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold tracking-tight text-foreground">DOCURA AI</span>
          <span className="hidden items-center gap-1.5 text-xs text-muted-foreground sm:flex">
            <span className="size-1.5 rounded-full bg-foreground/40" aria-hidden />
            Ready to help
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="hidden sm:block">
            <DocumentStatusCard documents={documents} loading={documentsLoading} />
          </div>
          <Button variant="outline" size="sm" onClick={newChat} disabled={pending}>
            <Plus className="size-4" aria-hidden />
            New chat
          </Button>
        </div>
      </header>

      {/* Message stream (or the welcome state when empty). */}
      <div ref={streamRef} className="chat-scroll relative flex-1 overflow-y-auto px-4 sm:px-6">
        <div className="pt-4 sm:hidden">
          <DocumentStatusCard documents={documents} loading={documentsLoading} className="sm:w-full" />
        </div>
        {empty ? (
          <WelcomeState onSelect={send} />
        ) : (
          <div className="mx-auto max-w-3xl space-y-5 py-6">
            {messages.map((m) => (
              <ChatMessage key={m.id} message={m} />
            ))}
            {pending ? <TypingIndicator /> : null}
          </div>
        )}
      </div>

      {/* Sticky composer + inline errors (never a stack trace). */}
      <div className="border-t border-white/8 bg-bg/70 px-4 py-4 backdrop-blur sm:px-6">
        <div className="mx-auto max-w-3xl space-y-2">
          {initError ? (
            <p role="alert" className="flex items-center justify-between gap-3 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-xs text-muted-foreground">
              <span>{initError}</span>
              <button
                type="button"
                onClick={() => setInitNonce((n) => n + 1)}
                className="shrink-0 font-medium text-foreground underline-offset-2 hover:underline"
              >
                Retry
              </button>
            </p>
          ) : null}
          {sendError ? (
            <p role="alert" className="flex items-center justify-between gap-3 rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-2 text-xs text-foreground">
              <span>{sendError}</span>
              <button
                type="button"
                onClick={() => send(lastText.current, false)}
                className="shrink-0 font-medium text-foreground underline-offset-2 hover:underline"
              >
                Try again
              </button>
            </p>
          ) : null}
          <ChatComposer onSubmit={send} loading={pending} disabled={initializing} />
        </div>
      </div>
    </div>
  );
}
