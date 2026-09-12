import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";

import { renderApp, sampleUser } from "@/test/render";
import type { DocumentResponse } from "@/lib/api";

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
});

describe("Command center (§5)", () => {
  it("shows the empty vault state with no documents", async () => {
    renderApp(["/app"]);
    expect(await screen.findByText(/document vault empty/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/upload a document to begin/i)).toBeInTheDocument();
  });

  it("shows the command interface when documents exist", async () => {
    m.listDocuments.mockResolvedValue({ documents: [doc()], count: 1 });
    renderApp(["/app"]);
    expect(await screen.findByText(/how can docura help/i)).toBeInTheDocument();
  });

  it("shows a processing state from real status", async () => {
    m.listDocuments.mockResolvedValue({ documents: [doc({ status: "processing" })], count: 1 });
    renderApp(["/app"]);
    expect(await screen.findByText(/document processing/i)).toBeInTheDocument();
  });

  it("shows a failed state with the reason, original still listed", async () => {
    m.listDocuments.mockResolvedValue({
      documents: [doc({ status: "failed", failure_reason: "unreadable scan" })],
      count: 1,
    });
    renderApp(["/app"]);
    expect(await screen.findByText(/processing failed/i)).toBeInTheDocument();
    expect(screen.getByText(/unreadable scan/i)).toBeInTheDocument();
  });
});

describe("Documents vault (§7)", () => {
  it("renders the empty state", async () => {
    renderApp(["/app/documents"]);
    expect(await screen.findByText(/no documents yet/i)).toBeInTheDocument();
  });

  it("lists documents", async () => {
    m.listDocuments.mockResolvedValue({ documents: [doc()], count: 1 });
    renderApp(["/app/documents"]);
    expect(await screen.findAllByText(/aadhaar\.pdf/i)).not.toHaveLength(0);
  });
});

describe("Document detail / understanding (§9)", () => {
  it("renders the header and an honest empty extraction state", async () => {
    m.getDocument.mockResolvedValue(doc());
    renderApp(["/app/documents/doc1"]);
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
    renderApp(["/app/documents/doc1"]);
    expect(await screen.findByText(/vedant kadam/i)).toBeInTheDocument();
    expect(screen.getByText(/92%/)).toBeInTheDocument(); // real confidence, not invented
  });
});

describe("My Record (§13)", () => {
  it("shows the empty record state", async () => {
    renderApp(["/app/record"]);
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
    renderApp(["/app/record"]);
    expect(await screen.findByText(/^Person$/)).toBeInTheDocument();
  });
});

describe("Activity (§15)", () => {
  it("shows the empty activity state", async () => {
    renderApp(["/app/activity"]);
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
    renderApp(["/app/activity"]);
    expect(await screen.findByText(/field filled/i)).toBeInTheDocument();
  });
});

describe("Settings (§16)", () => {
  it("renders account, security and data sections", async () => {
    renderApp(["/app/settings"]);
    expect(await screen.findByRole("button", { name: /sign out everywhere/i })).toBeInTheDocument();
    expect(screen.getByText(/account deletion not yet connected/i)).toBeInTheDocument();
  });
});

describe("Form session surfaces (§17/§18/§26/§24)", () => {
  beforeEach(() => {
    m.getFormSession.mockResolvedValue({ id: "sess1", state: "active", created_at: "2026-02-01T00:00:00Z", ended_at: null });
  });

  it("renders the session entry with lifecycle controls", async () => {
    renderApp(["/app/forms/sess1"]);
    expect(await screen.findByRole("button", { name: /hand back to me/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /stop session/i })).toBeInTheDocument();
  });

  it("renders the readiness seam", async () => {
    renderApp(["/app/forms/sess1/readiness"]);
    expect(await screen.findByText(/readiness is computed in the extension/i)).toBeInTheDocument();
  });

  it("renders the review with a hand-back panel (DOCURA does not submit)", async () => {
    renderApp(["/app/forms/sess1/review"]);
    expect(await screen.findByText(/docura does not submit the form/i)).toBeInTheDocument();
  });

  it("renders the approval seam (per-instance, no approve-all)", async () => {
    renderApp(["/app/forms/sess1/approval"]);
    expect(await screen.findByText(/one approval authorises exactly one disclosure/i)).toBeInTheDocument();
  });
});
