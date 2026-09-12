import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { renderApp, sampleUser } from "@/test/render";

vi.mock("@/lib/api", async (importActual) => {
  const actual = await importActual<typeof import("@/lib/api")>();
  return {
    ...actual,
    login: vi.fn(),
    register: vi.fn(),
    me: vi.fn(),
    logout: vi.fn(),
    requestPasswordReset: vi.fn(),
    confirmPasswordReset: vi.fn(),
    listDocuments: vi.fn(),
    getUploadLimits: vi.fn(),
    listFormSessions: vi.fn(),
  };
});

import * as api from "@/lib/api";
const mocked = api as unknown as {
  me: ReturnType<typeof vi.fn>;
  logout: ReturnType<typeof vi.fn>;
  listDocuments: ReturnType<typeof vi.fn>;
  getUploadLimits: ReturnType<typeof vi.fn>;
  listFormSessions: ReturnType<typeof vi.fn>;
};

// Simulate a signed-in browser: a stored token that /users/me accepts, with the command
// center's data calls resolving empty so the index page renders its zero-document state.
function signedIn() {
  localStorage.setItem("docura.token", "test-token");
  mocked.me.mockResolvedValue(sampleUser);
  mocked.listDocuments.mockResolvedValue({ documents: [], count: 0 });
  mocked.getUploadLimits.mockResolvedValue({
    accepted_media_types: ["application/pdf"],
    accepted_extensions: [".pdf", ".jpg", ".png"],
    max_document_bytes: 10485760,
    max_documents_per_upload: 5,
  });
  mocked.listFormSessions.mockResolvedValue({ sessions: [], count: 0 });
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe("Route protection", () => {
  // 9. Protected /app route redirects unauthenticated users to /login.
  it("redirects an unauthenticated user away from /app", async () => {
    renderApp(["/app"]);
    // No token → guard sends to /login; the login heading proves the redirect.
    expect(await screen.findByRole("heading", { name: /neural/i })).toBeInTheDocument();
    expect(mocked.me).not.toHaveBeenCalled();
  });

  // 10. Authenticated user can access /app.
  it("lets an authenticated user reach /app", async () => {
    signedIn();
    renderApp(["/app"]);
    expect(await screen.findByRole("heading", { name: /welcome back/i })).toBeInTheDocument();
    expect(mocked.me).toHaveBeenCalledWith("test-token");
  });

  // Bonus: an authenticated user visiting /login is redirected to /app.
  it("redirects an authenticated user away from /login", async () => {
    signedIn();
    renderApp(["/login"]);
    expect(await screen.findByRole("heading", { name: /welcome back/i })).toBeInTheDocument();
  });
});

describe("Application shell", () => {
  // 11. Logout ends the authenticated session (real backend call + redirect).
  it("signs out via the backend and returns to /login", async () => {
    const user = userEvent.setup();
    mocked.logout.mockResolvedValue({ revoked: 1 });
    signedIn();

    renderApp(["/app"]);
    await screen.findByRole("heading", { name: /welcome back/i });

    // The sidebar's Sign Out button is always in the DOM (desktop nav).
    await user.click(screen.getByRole("button", { name: /sign out/i }));

    await waitFor(() => expect(mocked.logout).toHaveBeenCalledWith("test-token"));
    expect(await screen.findByRole("heading", { name: /neural/i })).toBeInTheDocument();
    expect(localStorage.getItem("docura.token")).toBeNull();
  });

  // 12. Responsive navigation renders (mobile trigger + primary nav present).
  it("renders the primary navigation and the mobile nav trigger", async () => {
    signedIn();
    renderApp(["/app"]);
    await screen.findByRole("heading", { name: /welcome back/i });

    // Mobile drawer trigger exists (collapsed nav on small screens).
    expect(screen.getByRole("button", { name: /open navigation/i })).toBeInTheDocument();
    // Primary nav is present with the foundation destinations.
    const nav = screen.getByRole("navigation", { name: /primary/i });
    expect(nav).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /documents/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /activity/i })).toBeInTheDocument();
  });
});
