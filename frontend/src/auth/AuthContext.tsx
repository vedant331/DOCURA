// The one authentication/session mechanism for the web app (APP-1 §4/§9). It owns the
// bearer token and the current user, and exposes the four actions the UI needs. Route
// guards and the user menu read this — there is no second auth architecture.
//
// On mount it revalidates any stored token against GET /users/me: a token that the
// backend has since revoked (logout elsewhere, expiry, EC-016) must not present as a
// live session. While that check runs, `status` is "loading" so guards can wait
// instead of flashing the login screen.

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import * as api from "@/lib/api";
import type { UserResponse } from "@/lib/api";
import { clearToken, readToken, writeToken } from "@/auth/session";

type Status = "loading" | "authenticated" | "unauthenticated";

interface AuthContextValue {
  status: Status;
  user: UserResponse | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<Status>("loading");
  const [user, setUser] = useState<UserResponse | null>(null);
  const [token, setToken] = useState<string | null>(() => readToken());

  // Revalidate the stored token once on mount. A missing or rejected token → signed out.
  useEffect(() => {
    let cancelled = false;
    const stored = readToken();
    if (!stored) {
      setStatus("unauthenticated");
      return;
    }
    api
      .me(stored)
      .then((u) => {
        if (cancelled) return;
        setUser(u);
        setToken(stored);
        setStatus("authenticated");
      })
      .catch(() => {
        if (cancelled) return;
        clearToken();
        setToken(null);
        setUser(null);
        setStatus("unauthenticated");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    const result = await api.login(email, password);
    writeToken(result.access_token);
    setToken(result.access_token);
    setUser(result.user);
    setStatus("authenticated");
  }, []);

  // Register then sign in: the backend opens no session on registration (no token
  // returned), so the existing flow is create-account → authenticate.
  const signUp = useCallback(
    async (email: string, password: string) => {
      await api.register(email, password);
      await signIn(email, password);
    },
    [signIn],
  );

  const signOut = useCallback(async () => {
    const current = token ?? readToken();
    if (current) {
      try {
        await api.logout(current); // real server-side revocation, never fake local-only
      } catch {
        /* best-effort: the token is discarded regardless (fail toward inaction) */
      }
    }
    clearToken();
    setToken(null);
    setUser(null);
    setStatus("unauthenticated");
  }, [token]);

  const value = useMemo(
    () => ({ status, user, signIn, signUp, signOut }),
    [status, user, signIn, signUp, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
