import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import * as api from "@/lib/api";

// Cross-layer contract guard: exercises the REAL api.ts client (not the mocked module) against
// a stubbed fetch, asserting each call hits the exact backend route/method/body/headers and
// parses the response shape. This is the frontend half of the frontend→backend→database E2E
// (the backend half — real ASGI app + DB, ownership, no-submission — is covered by the pytest
// suite: test_chatbot, test_processing, test_extension_backend_contract).

const BASE = "http://127.0.0.1:8000";
const fetchMock = vi.fn();

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

function lastCall() {
  const [url, init] = fetchMock.mock.calls.at(-1) as [string, RequestInit];
  return { url, init, headers: (init.headers ?? {}) as Record<string, string> };
}

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
  localStorage.clear();
  localStorage.setItem("docura.token", "tok-123");
});
afterEach(() => vi.unstubAllGlobals());

describe("chat API contract (frontend ↔ backend/app/api/chat.py)", () => {
  it("createConversation POSTs /conversations with auth + a json body", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse({ id: "c1", title: "New chat", created_at: "t", updated_at: "t" }, 201),
    );
    const conv = await api.createConversation();
    const { url, init, headers } = lastCall();
    expect(url).toBe(`${BASE}/conversations`);
    expect(init.method).toBe("POST");
    expect(headers.Authorization).toBe("Bearer tok-123");
    expect(headers["Content-Type"]).toBe("application/json");
    expect(JSON.parse(String(init.body))).toEqual({ title: null });
    expect(conv.id).toBe("c1");
  });

  it("sendMessage POSTs {content} to the conversation and returns the turn", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(
        {
          user_message: { id: "u1", role: "user", message_type: "text", content: "hi", data: null, created_at: "t" },
          assistant_message: { id: "a1", role: "assistant", message_type: "text", content: "Hello.", data: null, created_at: "t" },
        },
        201,
      ),
    );
    const turn = await api.sendMessage("c1", "hi");
    const { url, init } = lastCall();
    expect(url).toBe(`${BASE}/conversations/c1/messages`);
    expect(init.method).toBe("POST");
    expect(JSON.parse(String(init.body))).toEqual({ content: "hi" });
    expect(turn.assistant_message.content).toBe("Hello.");
  });

  it("listMessages GETs the paginated route with auth", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ messages: [], count: 0 }));
    await api.listMessages("c1");
    const { url, headers } = lastCall();
    expect(url).toBe(`${BASE}/conversations/c1/messages?limit=100&offset=0`);
    expect(headers.Authorization).toBe("Bearer tok-123");
  });

  it("deleteConversation DELETEs and tolerates a 204 (no body)", async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => {
        throw new Error("no body");
      },
    } as unknown as Response);
    await expect(api.deleteConversation("c1")).resolves.toBeUndefined();
    const { url, init } = lastCall();
    expect(url).toBe(`${BASE}/conversations/c1`);
    expect(init.method).toBe("DELETE");
  });

  it("surfaces a problem+json detail as an ApiError with the status", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ detail: "Conversation not found." }, 404));
    await expect(api.getConversation("nope")).rejects.toMatchObject({
      name: "ApiError",
      status: 404,
      message: "Conversation not found.",
    });
  });
});

describe("account deletion contract (DELETE /users/me)", () => {
  it("DELETEs /users/me with the confirmation email in the body", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse({ status: "deleted", email: "a@b.co", documents_removed: 0, objects_removed: 0 }),
    );
    await api.deleteAccount("a@b.co");
    const { url, init, headers } = lastCall();
    expect(url).toBe(`${BASE}/users/me`);
    expect(init.method).toBe("DELETE");
    expect(headers["Content-Type"]).toBe("application/json");
    expect(JSON.parse(String(init.body))).toEqual({ confirm_email: "a@b.co" });
  });
});

describe("search + export contract", () => {
  it("search GETs /search with the URL-encoded query and auth", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse({ query: "voter id", documents: [], attributes: [], document_count: 0, attribute_count: 0 }),
    );
    await api.search("voter id");
    const { url, headers } = lastCall();
    expect(url).toBe(`${BASE}/search?q=voter%20id`);
    expect(headers.Authorization).toBe("Bearer tok-123");
  });

  it("exportRecord GETs /record/export with auth and returns a Blob", async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      status: 200,
      blob: async () => new Blob(["{}"], { type: "application/json" }),
    } as unknown as Response);
    const blob = await api.exportRecord();
    const { url } = lastCall();
    expect(url).toBe(`${BASE}/record/export`);
    expect(blob).toBeInstanceOf(Blob);
  });
});

describe("auth is required for owner-scoped calls", () => {
  it("throws a 401 ApiError before any fetch when no token is stored", () => {
    localStorage.clear();
    // authInit throws synchronously (before returning a promise), so assert a sync throw.
    let caught: unknown;
    try {
      void api.listConversations();
    } catch (e) {
      caught = e;
    }
    expect(caught).toMatchObject({ name: "ApiError", status: 401 });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
