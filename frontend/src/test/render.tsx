import { type ReactElement } from "react";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import App from "@/App";
import { AuthProvider } from "@/auth/AuthContext";
import { GreetingProvider } from "@/components/auth/greeting-context";

// Render the whole routed app at a chosen location, wrapped in the real AuthProvider +
// GreetingProvider so route guards and session behaviour are exercised end to end (only the
// network layer, @/lib/api, is mocked in the tests themselves).
export function renderApp(initialEntries: string[] = ["/login"]) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <AuthProvider>
        <GreetingProvider>
          <App />
        </GreetingProvider>
      </AuthProvider>
    </MemoryRouter>,
  );
}

// Render an arbitrary element inside just the router + auth provider (for a single page).
export function renderWithProviders(ui: ReactElement, initialEntries: string[] = ["/"]) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <AuthProvider>
        <GreetingProvider>{ui}</GreetingProvider>
      </AuthProvider>
    </MemoryRouter>,
  );
}

export const sampleUser = {
  id: "00000000-0000-0000-0000-000000000001",
  email: "operator@docura.test",
  is_active: true,
  created_at: "2026-01-01T00:00:00Z",
};

export const sampleLogin = {
  access_token: "test-token",
  token_type: "bearer" as const,
  expires_at: "2099-01-01T00:00:00Z",
  user: sampleUser,
};
