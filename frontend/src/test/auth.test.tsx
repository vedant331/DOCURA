import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { renderApp, sampleLogin } from "@/test/render";

// Mock only the network layer; keep ApiError real so `instanceof` branches work.
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
  };
});

import * as api from "@/lib/api";
const mocked = api as unknown as {
  login: ReturnType<typeof vi.fn>;
  register: ReturnType<typeof vi.fn>;
  me: ReturnType<typeof vi.fn>;
  requestPasswordReset: ReturnType<typeof vi.fn>;
  confirmPasswordReset: ReturnType<typeof vi.fn>;
};

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe("Login", () => {
  // 1. Login page renders.
  it("renders the login form", async () => {
    renderApp(["/login"]);
    expect(await screen.findByRole("heading", { name: /neural/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/user identity/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/sequence key/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /initialize stream/i })).toBeInTheDocument();
  });

  // 2. Login validation works.
  it("shows validation errors and does not call the API on empty submit", async () => {
    const user = userEvent.setup();
    renderApp(["/login"]);
    await user.click(await screen.findByRole("button", { name: /initialize stream/i }));
    expect(await screen.findByText(/enter your user identity/i)).toBeInTheDocument();
    expect(screen.getByText(/enter your sequence key/i)).toBeInTheDocument();
    expect(mocked.login).not.toHaveBeenCalled();
  });

  // 3. Login loading state works.
  it("disables the button and shows a loading label while submitting", async () => {
    const user = userEvent.setup();
    let resolve!: (v: typeof sampleLogin) => void;
    mocked.login.mockReturnValue(new Promise((r) => (resolve = r)));

    renderApp(["/login"]);
    await user.type(screen.getByLabelText(/user identity/i), "operator@docura.test");
    await user.type(screen.getByLabelText(/sequence key/i), "hunter2hunter2");
    await user.click(screen.getByRole("button", { name: /initialize stream/i }));

    const btn = await screen.findByRole("button", { name: /initializing/i });
    expect(btn).toBeDisabled();
    resolve(sampleLogin); // let it finish so the test exits cleanly
    await waitFor(() => expect(mocked.login).toHaveBeenCalled());
  });

  // 4. Login backend error displays correctly.
  it("shows a backend error for invalid credentials", async () => {
    const user = userEvent.setup();
    mocked.login.mockRejectedValue(new api.ApiError("nope", 401));

    renderApp(["/login"]);
    await user.type(screen.getByLabelText(/user identity/i), "operator@docura.test");
    await user.type(screen.getByLabelText(/sequence key/i), "wrongpass");
    await user.click(screen.getByRole("button", { name: /initialize stream/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/not accepted/i);
  });

  // 5. Successful login redirects to /app.
  it("redirects to /app on successful login", async () => {
    const user = userEvent.setup();
    mocked.login.mockResolvedValue(sampleLogin);

    renderApp(["/login"]);
    await user.type(screen.getByLabelText(/user identity/i), "operator@docura.test");
    await user.type(screen.getByLabelText(/sequence key/i), "hunter2hunter2");
    await user.click(screen.getByRole("button", { name: /initialize stream/i }));

    expect(await screen.findByRole("heading", { name: /welcome back/i })).toBeInTheDocument();
    expect(localStorage.getItem("docura.token")).toBe("test-token");
  });
});

describe("Register", () => {
  // 6. Register page renders and validates.
  it("renders and validates the confirm-password mismatch", async () => {
    const user = userEvent.setup();
    renderApp(["/register"]);
    expect(await screen.findByRole("heading", { name: /create/i })).toBeInTheDocument();

    await user.type(screen.getByLabelText(/^email$/i), "new@docura.test");
    await user.type(screen.getByLabelText(/^sequence key$/i), "abcdefgh12");
    await user.type(screen.getByLabelText(/confirm sequence key/i), "different");
    await user.click(screen.getByRole("button", { name: /create identity/i }));

    expect(await screen.findByText(/do not match/i)).toBeInTheDocument();
    expect(mocked.register).not.toHaveBeenCalled();
  });

  it("registers then signs in and lands on /app", async () => {
    const user = userEvent.setup();
    mocked.register.mockResolvedValue(sampleLogin.user);
    mocked.login.mockResolvedValue(sampleLogin);

    renderApp(["/register"]);
    await user.type(await screen.findByLabelText(/^email$/i), "new@docura.test");
    await user.type(screen.getByLabelText(/^sequence key$/i), "abcdefgh12");
    await user.type(screen.getByLabelText(/confirm sequence key/i), "abcdefgh12");
    await user.click(screen.getByRole("button", { name: /create identity/i }));

    expect(await screen.findByRole("heading", { name: /welcome back/i })).toBeInTheDocument();
    expect(mocked.register).toHaveBeenCalledWith("new@docura.test", "abcdefgh12");
  });
});

describe("Forgot password", () => {
  // 7. Forgot password page renders.
  it("renders and shows a processed state on submit", async () => {
    const user = userEvent.setup();
    mocked.requestPasswordReset.mockResolvedValue({ status: "accepted", detail: "ok" });

    renderApp(["/forgot-password"]);
    expect(await screen.findByRole("heading", { name: /recover/i })).toBeInTheDocument();

    await user.type(screen.getByLabelText(/account email/i), "operator@docura.test");
    await user.click(screen.getByRole("button", { name: /dispatch recovery/i }));

    expect(await screen.findByText(/request processed/i)).toBeInTheDocument();
    expect(mocked.requestPasswordReset).toHaveBeenCalledWith("operator@docura.test");
  });
});

describe("Reset password", () => {
  // 8. Reset password page renders (with a token) and shows expired state without one.
  it("renders the reset form when a token is present", async () => {
    renderApp(["/reset-password?token=abc123"]);
    expect(await screen.findByRole("heading", { name: /set new/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/new sequence key/i)).toBeInTheDocument();
  });

  it("shows the expired-link state when no token is present", async () => {
    renderApp(["/reset-password"]);
    expect(await screen.findByText(/invalid or expired link/i)).toBeInTheDocument();
  });

  it("confirms a reset and shows the success state", async () => {
    const user = userEvent.setup();
    mocked.confirmPasswordReset.mockResolvedValue({ status: "reset", sessions_revoked: 2 });

    renderApp(["/reset-password?token=abc123"]);
    await user.type(await screen.findByLabelText(/new sequence key/i), "brandnewkey1");
    await user.type(screen.getByLabelText(/confirm sequence key/i), "brandnewkey1");
    await user.click(screen.getByRole("button", { name: /reset sequence key/i }));

    expect(await screen.findByText(/sequence key updated/i)).toBeInTheDocument();
    expect(mocked.confirmPasswordReset).toHaveBeenCalledWith("abc123", "brandnewkey1");
  });
});
