import { useState } from "react";

import { ChatComposer } from "@/components/command/ChatComposer";
import {
  AssistantState,
  ChatMessage,
  EmptyConversationState,
  type ChatMessageData,
} from "@/components/command/ChatPieces";

const SUGGESTED = [
  "What documents do I still need for a typical application?",
  "Summarise what DOCURA has read from my documents.",
  "Which of my details are missing or need review?",
  "Show me everything sourced from my ID document.",
];

// The reusable chat surface (§6). It records the user's messages, but because no assistant
// endpoint exists it responds with an explicit not-connected system note — never a
// fabricated answer. Designed so a real assistant can be wired in by replacing the
// system-note step with a streamed response, with no layout change.
export function ChatWorkspace({ contextCount }: { contextCount: number }) {
  const [messages, setMessages] = useState<ChatMessageData[]>([]);

  const submit = (text: string) => {
    const userMsg: ChatMessageData = { id: crypto.randomUUID(), role: "user", text };
    const notConnected: ChatMessageData = {
      id: crypto.randomUUID(),
      role: "system",
      text: "Assistant not connected — no answer was generated.",
    };
    setMessages((prev) => [...prev, userMsg, notConnected]);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="min-h-[8rem] space-y-2">
        {messages.length === 0 ? (
          <EmptyConversationState prompts={SUGGESTED} onSelect={submit} />
        ) : (
          messages.map((m) => <ChatMessage key={m.id} message={m} />)
        )}
      </div>
      <AssistantState />
      <ChatComposer onSubmit={submit} contextCount={contextCount} />
    </div>
  );
}
