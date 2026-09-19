import type { MessageResponse } from "@/lib/api";

// The chat message model + the adapter that turns a backend assistant message into UI blocks.
// The backend is the source of truth: this file NEVER generates an answer — it only maps the
// server's structured `data` (statuses, references, actions — value-free) onto reusable blocks.

export type ChatRole = "user" | "assistant";

export type RequirementStatus =
  | "available"
  | "missing"
  | "needs_approval"
  | "needs_review"
  | "unknown";

export interface RequirementItem {
  label: string;
  status: RequirementStatus;
  note?: string;
}

export interface ActionItem {
  label: string;
  to?: string; // in-app route (only for actions that map to a web destination)
  variant?: "primary" | "outline";
}

// The structured blocks an assistant message can render. Reusable response building blocks.
export type AssistantBlock =
  | { kind: "text"; text: string }
  | { kind: "heading"; text: string }
  | { kind: "requirements"; items: RequirementItem[] }
  | { kind: "actions"; items: ActionItem[] }
  | { kind: "warning"; text: string }
  | { kind: "approval"; text: string };

export type MessageType = "text" | "structured" | "loading";

export interface ChatMessageData {
  id: string;
  role: ChatRole;
  type: MessageType;
  text?: string; // for role "user" and simple text messages
  blocks?: AssistantBlock[]; // for structured assistant messages
  timestamp: number;
}

// Optimistic echo of what the user typed (shown immediately; the server persists the same text).
export function userMessage(text: string): ChatMessageData {
  return { id: crypto.randomUUID(), role: "user", type: "text", text, timestamp: Date.now() };
}

// ---- backend → UI adapter --------------------------------------------------------------

// Only actions that have a real in-app destination get a route; page/extension actions
// (open_form, start_form_session) render as informational, never faking a navigation.
const ACTION_ROUTES: Record<string, string> = {
  view_documents: "/app/documents",
  open_documents: "/app/documents",
  open_record: "/app/record",
};

const REQUIREMENT_STATUSES: RequirementStatus[] = [
  "available",
  "missing",
  "needs_approval",
  "needs_review",
  "unknown",
];

function asRecord(v: unknown): Record<string, unknown> | null {
  return v && typeof v === "object" && !Array.isArray(v) ? (v as Record<string, unknown>) : null;
}
function asArray(v: unknown): unknown[] {
  return Array.isArray(v) ? v : [];
}
function asString(v: unknown): string {
  return typeof v === "string" ? v : "";
}
function toStatus(v: unknown): RequirementStatus {
  return REQUIREMENT_STATUSES.includes(v as RequirementStatus) ? (v as RequirementStatus) : "unknown";
}

// Document processing status → a requirement-style status, for display only.
function docStatus(status: string): RequirementStatus {
  if (status === "ready") return "available";
  if (status === "needs_review") return "needs_review";
  if (status === "failed") return "missing";
  return "unknown"; // queued | processing | unknown
}

// Map ONE backend assistant/system message to a renderable chat message. Every block is
// derived from server data; nothing is fabricated. If a section is absent, no block is made.
export function toAssistantMessage(m: MessageResponse): ChatMessageData {
  const data = asRecord(m.data) ?? {};
  const blocks: AssistantBlock[] = [];
  let text: string | undefined = m.content;

  switch (m.message_type) {
    case "readiness": {
      const readiness = asRecord(data.readiness);
      const items = asArray(readiness?.items)
        .map((it) => {
          const o = asRecord(it) ?? {};
          return {
            label: asString(o.label),
            status: toStatus(o.status),
            note: asString(o.note) || undefined,
          };
        })
        .filter((i) => i.label);
      if (items.length) blocks.push({ kind: "requirements", items });
      break;
    }
    case "document_status": {
      const items = asArray(data.documents)
        .map((d) => {
          const o = asRecord(d) ?? {};
          const status = asString(o.status);
          return {
            label: asString(o.filename) || "Document",
            status: docStatus(status),
            note: status || undefined,
          };
        })
        .filter((i) => i.label);
      if (items.length) blocks.push({ kind: "requirements", items });
      break;
    }
    case "requirements": {
      const req = asRecord(data.requirements);
      const labels = [...asArray(req?.documents), ...asArray(req?.information)]
        .map((it) => asString(asRecord(it)?.label))
        .filter(Boolean);
      if (labels.length) {
        blocks.push({
          kind: "requirements",
          items: labels.map((label) => ({ label, status: "unknown" as RequirementStatus })),
        });
      }
      break;
    }
    case "approval": {
      blocks.push({ kind: "approval", text: m.content });
      text = undefined;
      break;
    }
    case "error": {
      blocks.push({ kind: "warning", text: m.content });
      text = undefined;
      break;
    }
    default:
      break; // text | question | action → the content string carries the message
  }

  const actions = asArray(data.actions)
    .map((a) => {
      const o = asRecord(a) ?? {};
      const type = asString(o.type);
      return { label: asString(o.label) || type, to: ACTION_ROUTES[type] } as ActionItem;
    })
    .filter((a) => a.label);
  if (actions.length) {
    const firstRouted = actions.findIndex((a) => a.to);
    if (firstRouted >= 0) actions[firstRouted] = { ...actions[firstRouted], variant: "primary" };
    blocks.push({ kind: "actions", items: actions });
  }

  return {
    id: m.id,
    role: "assistant",
    type: blocks.length ? "structured" : "text",
    text,
    blocks,
    timestamp: Date.parse(m.created_at) || Date.now(),
  };
}

// Map any persisted message (user or assistant/system) for rendering history.
export function toChatMessage(m: MessageResponse): ChatMessageData {
  if (m.role === "user") {
    return {
      id: m.id,
      role: "user",
      type: "text",
      text: m.content,
      timestamp: Date.parse(m.created_at) || Date.now(),
    };
  }
  return toAssistantMessage(m);
}
