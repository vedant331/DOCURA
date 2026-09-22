import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { renderApp, sampleUser } from "@/test/render";
import { ApiError } from "@/lib/api";
import type { DocumentResponse, MessageResponse } from "@/lib/api";

// Mock only the network layer; keep ApiError real for instanceof branches.
vi.mock("@/lib/api", async (importActual) => {
  const actual = await importActual<typeof import("@/lib/api")>();
  return {
    ...actual,
    me: vi.fn(),
    listDocuments: vi.fn(),
    getUploadLimits: vi.fn(),
    listFormSessions: vi.fn(),
    getFormSession: vi.fn(),
    getFormSessionActions: vi.fn(),
    getDocument: vi.fn(),
    getRecord: vi.fn(),
    listAuthSessions: vi.fn(),
    downloadDocument: vi.fn(),
    logout: vi.fn(),
    listConversations: vi.fn(),
    createConversation: vi.fn(),
    getConversation: vi.fn(),
    renameConversation: vi.fn(),
    deleteConversation: vi.fn(),
    sendMessage: vi.fn(),
    listMessages: vi.fn(),
    deleteAccount: vi.fn(),
    exportRecord: vi.fn(),
    search: vi.fn(),
  };
});

import * as api from "@/lib/api";
const m = api as unknown as Record<string, ReturnType<typeof vi.fn>>;

const LIMITS = {
  accepted_media_types: ["application/pdf"],
  accepted_extensions: [".pdf", ".jpg", ".png"],
  max_document_bytes: 10485760,
  max_documents_per_upload: 5,
};

function doc(overrides: Partial<DocumentResponse> = {}): DocumentResponse {
  return {
    id: "doc1",
    original_filename: "aadhaar.pdf",
    content_type: "application/pdf",
    byte_size: 2048,
    checksum_sha256: "abc",
    document_type: "unclassified",
    status: "ready",
    failure_reason: null,
    created_at: "2026-02-01T10:00:00Z",
    updated_at: "2026-02-01T10:00:00Z",
    ...overrides,
  };
}

const CONV = { id: "c1", title: "New chat", created_at: "2026-02-01T10:00:00Z", updated_at: "2026-02-01T10:00:00Z" };

function msg(overrides: Partial<MessageResponse> = {}): MessageResponse {
  return {
    id: "mX",
    role: "assistant",
    message_type: "text",
    content: "Hello from DOCURA.",
    data: null,
    created_at: "2026-02-01T10:00:00Z",
    ...overrides,
  };
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  localStorage.setItem("docura.token", "test-token");
  m.me.mockResolvedValue(sampleUser);
  // Sensible empty defaults; individual tests override.
  m.listDocuments.mockResolvedValue({ documents: [], count: 0 });
  m.getUploadLimits.mockResolvedValue(LIMITS);
  m.listFormSessions.mockResolvedValue({ sessions: [], count: 0 });
  m.getFormSessionActions.mockResolvedValue({ actions: [], count: 0 });
  m.getRecord.mockResolvedValue({ attributes: [], count: 0 });
  m.listAuthSessions.mockResolvedValue({ sessions: [] });
  m.downloadDocument.mockResolvedValue(new Blob(["x"], { type: "application/pdf" }));
  m.logout.mockResolvedValue({ revoked: 1 });
  // Chat defaults: no prior conversation → a fresh one is created; sends echo a text reply.
  m.listConversations.mockResolvedValue({ conversations: [], count: 0 });
  m.createConversation.mockResolvedValue(CONV);
  m.listMessages.mockResolvedValue({ messages: [], count: 0 });
  m.sendMessage.mockResolvedValue({
    user_message: msg({ id: "u1", role: "user", content: "hi" }),
    assistant_message: msg({ id: "a1", content: "Hello from DOCURA." }),
  });
  m.deleteAccount.mockResolvedValue({ email: sampleUser.email, documents_removed: 0, objects_removed: 0 });
  m.exportRecord.mockResolvedValue(new Blob(['{"docura_export_version":"1"}'], { type: "application/json" }));
  m.search.mockResolvedValue({ query: "", documents: [], attributes: [], document_count: 0, attribute_count: 0 });
});

describe("Command center — AI chat workspace (§5)", () => {
  it("shows the welcome + composer + New chat, with the old status strip removed", async () => {
    renderApp(["/ask"]);
    // The chat is the primary surface (composer always present) with the welcome state.
    expect(await screen.findByPlaceholderText(/ask docura anything/i)).toBeInTheDocument();
    expect(screen.getByText(/how can docura help/i)).toBeInTheDocument();
    // New chat is preserved.
    expect(screen.getByRole("button", { name: /new chat/i })).toBeInTheDocument();
    // The removed header/status strip and document-status card are gone from this area.
    expect(screen.queryByText(/docura ai/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/ready to help/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/documents ready/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/documents? available/i)).not.toBeInTheDocument();
  });

  it("creates a conversation on load and sends messages to the backend", async () => {
    const user = userEvent.setup();
    renderApp(["/ask"]);
    const composer = await screen.findByPlaceholderText(/ask docura anything/i);
    // A real backend conversation is created (never a frontend-only fake).
    await waitFor(() => expect(m.createConversation).toHaveBeenCalledTimes(1));
    await user.type(composer, "Hello DOCURA");
    await user.keyboard("{Enter}");
    // The message goes to the backend and the backend's reply is rendered (no local AI).
    await waitFor(() => expect(m.sendMessage).toHaveBeenCalledWith("c1", "Hello DOCURA"));
    expect(await screen.findByText(/hello from docura/i)).toBeInTheDocument();
  });

  it("renders the backend's structured readiness reply", async () => {
    const user = userEvent.setup();
    m.sendMessage.mockResolvedValue({
      user_message: msg({ id: "u1", role: "user", content: "Am I ready?" }),
      assistant_message: msg({
        id: "a1",
        message_type: "readiness",
        content: "You're not ready yet — some required items are missing or need review.",
        data: {
          readiness: {
            items: [
              { label: "Full name", status: "available" },
              { label: "Date of birth", status: "needs_approval" },
            ],
          },
        },
      }),
    });
    renderApp(["/ask"]);
    const composer = await screen.findByPlaceholderText(/ask docura anything/i);
    await user.type(composer, "Am I ready?");
    await user.keyboard("{Enter}");
    expect(await screen.findByText(/not ready yet/i)).toBeInTheDocument();
    expect(screen.getByText(/full name/i)).toBeInTheDocument();
    expect(screen.getByText(/date of birth/i)).toBeInTheDocument();
    expect(screen.getByText(/needs approval/i)).toBeInTheDocument();
  });

  it("restores the most recent conversation and its messages on load", async () => {
    m.listConversations.mockResolvedValue({
      conversations: [{ id: "cX", title: "Earlier", created_at: "2026-02-01T09:00:00Z", updated_at: "2026-02-01T09:30:00Z" }],
      count: 1,
    });
    m.listMessages.mockResolvedValue({
      messages: [
        msg({ id: "m1", role: "user", content: "earlier question" }),
        msg({ id: "m2", role: "assistant", content: "earlier answer" }),
      ],
      count: 2,
    });
    renderApp(["/ask"]);
    expect(await screen.findByText(/earlier question/i)).toBeInTheDocument();
    expect(screen.getByText(/earlier answer/i)).toBeInTheDocument();
    await waitFor(() => expect(m.listMessages).toHaveBeenCalledWith("cX"));
    expect(m.createConversation).not.toHaveBeenCalled(); // restored, not recreated
  });

  it("creates a new backend conversation from the New chat button", async () => {
    const user = userEvent.setup();
    renderApp(["/ask"]);
    await screen.findByPlaceholderText(/ask docura anything/i);
    await waitFor(() => expect(m.createConversation).toHaveBeenCalledTimes(1)); // on load
    await user.click(screen.getByRole("button", { name: /new chat/i }));
    await waitFor(() => expect(m.createConversation).toHaveBeenCalledTimes(2)); // explicit new
  });

  it("shows an inline error when a send fails and can retry", async () => {
    const user = userEvent.setup();
    m.sendMessage.mockRejectedValueOnce(new ApiError("Cannot reach DOCURA. Check your connection and try again.", 0));
    renderApp(["/ask"]);
    const composer = await screen.findByPlaceholderText(/ask docura anything/i);
    await user.type(composer, "hello");
    await user.keyboard("{Enter}");
    expect(await screen.findByText(/cannot reach docura/i)).toBeInTheDocument();
    // Retry succeeds using the default resolved mock.
    await user.click(screen.getByRole("button", { name: /try again/i }));
    expect(await screen.findByText(/hello from docura/i)).toBeInTheDocument();
  });
});

describe("Documents vault (§7)", () => {
  it("renders the empty state", async () => {
    renderApp(["/documents"]);
    expect(await screen.findByText(/no documents yet/i)).toBeInTheDocument();
  });

  it("lists documents", async () => {
    m.listDocuments.mockResolvedValue({ documents: [doc()], count: 1 });
    renderApp(["/documents"]);
    expect(await screen.findAllByText(/aadhaar\.pdf/i)).not.toHaveLength(0);
  });

  it("searches documents and record, and renders matches (FR-SRCH)", async () => {
    const user = userEvent.setup();
    m.search.mockResolvedValue({
      query: "priya",
      documents: [{ id: "doc1", original_filename: "aadhaar.pdf", status: "ready" }],
      attributes: [
        { canonical_identifier: "person.full_name", value: "Priya Sharma", is_ambiguous: false, document_id: "doc1", page_number: 1 },
      ],
      document_count: 1,
      attribute_count: 1,
    });
    renderApp(["/documents"]);
    const box = await screen.findByRole("searchbox", { name: /search documents and your record/i });
    await user.type(box, "priya");
    await user.keyboard("{Enter}");
    await waitFor(() => expect(m.search).toHaveBeenCalledWith("priya"));
    expect(await screen.findByText(/person\.full_name: Priya Sharma/i)).toBeInTheDocument();
    // Attribute match links to the record; document match links to its detail page.
    expect(screen.getByRole("link", { name: /person\.full_name/i })).toHaveAttribute("href", "/record");
  });

  it("shows an empty search state when nothing matches", async () => {
    const user = userEvent.setup();
    m.search.mockResolvedValue({ query: "zzz", documents: [], attributes: [], document_count: 0, attribute_count: 0 });
    renderApp(["/documents"]);
    const box = await screen.findByRole("searchbox");
    await user.type(box, "zzz");
    await user.keyboard("{Enter}");
    expect(await screen.findByText(/no matches for/i)).toBeInTheDocument();
  });

  it("shows a search error state on API failure", async () => {
    const user = userEvent.setup();
    m.search.mockRejectedValue(new ApiError("Search failed. Try again.", 500));
    renderApp(["/documents"]);
    const box = await screen.findByRole("searchbox");
    await user.type(box, "boom");
    await user.keyboard("{Enter}");
    expect(await screen.findByText(/search failed/i)).toBeInTheDocument();
  });
});

describe("Document detail / understanding (§9)", () => {
  it("renders the header and an honest empty extraction state", async () => {
    m.getDocument.mockResolvedValue(doc());
    renderApp(["/documents/doc1"]);
    expect(await screen.findByRole("heading", { name: /aadhaar\.pdf/i })).toBeInTheDocument();
    expect(await screen.findByText(/no extracted information yet/i)).toBeInTheDocument();
  });

  it("renders extracted values with provenance when present", async () => {
    m.getDocument.mockResolvedValue(doc());
    m.getRecord.mockResolvedValue({
      attributes: [
        {
          canonical_identifier: "person.full_name",
          value: "Vedant Kadam",
          is_ambiguous: false,
          observations: [
            { value: "Vedant Kadam", confidence: 0.92, document_id: "doc1", extraction_run_id: "r1", page_number: 1, region: null },
          ],
        },
      ],
      count: 1,
    });
    renderApp(["/documents/doc1"]);
    expect(await screen.findByText(/vedant kadam/i)).toBeInTheDocument();
    expect(screen.getByText(/92%/)).toBeInTheDocument(); // real confidence, not invented
  });
});

describe("My Record (§13)", () => {
  it("shows the empty record state", async () => {
    renderApp(["/record"]);
    expect(await screen.findByText(/no record data yet/i)).toBeInTheDocument();
  });

  it("groups attributes and flags conflicts", async () => {
    m.getRecord.mockResolvedValue({
      attributes: [
        {
          canonical_identifier: "person.date_of_birth",
          value: null,
          is_ambiguous: true,
          observations: [
            { value: "1990-01-01", confidence: 0.8, document_id: "doc1", extraction_run_id: "r1", page_number: 1, region: null },
            { value: "1991-01-01", confidence: 0.8, document_id: "doc2", extraction_run_id: "r2", page_number: 1, region: null },
          ],
        },
      ],
      count: 1,
    });
    renderApp(["/record"]);
    expect(await screen.findByText(/^Person$/)).toBeInTheDocument();
  });

  it("exports the record via the backend (FR-ACC-006)", async () => {
    const user = userEvent.setup();
    // jsdom lacks object-URL APIs the download path uses.
    const createURL = vi.fn(() => "blob:mock");
    const revokeURL = vi.fn();
    vi.stubGlobal("URL", { ...URL, createObjectURL: createURL, revokeObjectURL: revokeURL });
    renderApp(["/record"]);
    await user.click(await screen.findByRole("button", { name: /export/i }));
    await waitFor(() => expect(m.exportRecord).toHaveBeenCalledTimes(1));
    expect(createURL).toHaveBeenCalled();
    vi.unstubAllGlobals();
  });
});

describe("Activity (§15)", () => {
  it("shows the empty activity state", async () => {
    renderApp(["/activity"]);
    expect(await screen.findByText(/no activity yet/i)).toBeInTheDocument();
  });

  it("renders a read-only timeline from session actions", async () => {
    m.listFormSessions.mockResolvedValue({ sessions: [{ id: "s1", state: "active", created_at: "2026-02-01T00:00:00Z", ended_at: null }], count: 1 });
    m.getFormSessionActions.mockResolvedValue({
      actions: [
        { id: "a1", action_type: "fill", outcome: "succeeded", field_ref: "#name", document_id: null, observation_id: null, reverses_action_id: null, detail: "filled name", created_at: "2026-02-01T01:00:00Z" },
      ],
      count: 1,
    });
    renderApp(["/activity"]);
    expect(await screen.findByText(/field filled/i)).toBeInTheDocument();
  });
});

describe("Settings (§16)", () => {
  it("renders account, security and data sections", async () => {
    renderApp(["/settings"]);
    expect(await screen.findByRole("button", { name: /sign out everywhere/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^delete account$/i })).toBeInTheDocument();
  });

  it("deletes the account after email confirmation, then signs out to /login", async () => {
    const user = userEvent.setup();
    renderApp(["/settings"]);
    await user.click(await screen.findByRole("button", { name: /^delete account$/i }));

    const dialog = await screen.findByRole("dialog");
    const confirm = within(dialog).getByRole("button", { name: /delete account/i });
    // Confirm is disabled until the typed email matches the account email.
    expect(confirm).toBeDisabled();
    await user.type(within(dialog).getByLabelText(/confirm your email/i), sampleUser.email);
    expect(confirm).toBeEnabled();
    await user.click(confirm);

    await waitFor(() => expect(m.deleteAccount).toHaveBeenCalledWith(sampleUser.email));
    // Session cleared + returned to the sign-in screen.
    await waitFor(() => expect(localStorage.getItem("docura.token")).toBeNull());
  });

  it("does not delete when the confirmation email does not match", async () => {
    const user = userEvent.setup();
    renderApp(["/settings"]);
    await user.click(await screen.findByRole("button", { name: /^delete account$/i }));
    const dialog = await screen.findByRole("dialog");
    await user.type(within(dialog).getByLabelText(/confirm your email/i), "wrong@example.com");
    expect(within(dialog).getByRole("button", { name: /delete account/i })).toBeDisabled();
    expect(m.deleteAccount).not.toHaveBeenCalled();
  });
});

describe("Form session surfaces (§17/§18/§26/§24)", () => {
  beforeEach(() => {
    m.getFormSession.mockResolvedValue({ id: "sess1", state: "active", created_at: "2026-02-01T00:00:00Z", ended_at: null });
  });

  it("renders the session entry with lifecycle controls", async () => {
    renderApp(["/forms/sess1"]);
    expect(await screen.findByRole("button", { name: /hand back to me/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /stop session/i })).toBeInTheDocument();
  });

  it("renders the readiness seam", async () => {
    renderApp(["/forms/sess1/readiness"]);
    expect(await screen.findByText(/readiness is computed in the extension/i)).toBeInTheDocument();
  });

  it("renders the review with a hand-back panel (DOCURA does not submit)", async () => {
    renderApp(["/forms/sess1/review"]);
    expect(await screen.findByText(/docura does not submit the form/i)).toBeInTheDocument();
  });

  it("renders the approval seam (per-instance, no approve-all)", async () => {
    renderApp(["/forms/sess1/approval"]);
    expect(await screen.findByText(/one approval authorises exactly one disclosure/i)).toBeInTheDocument();
  });
});
