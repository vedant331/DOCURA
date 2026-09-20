import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "@/auth/AuthContext";
import { AuthLoadingState } from "@/components/auth/AuthLoadingState";
import { useGreeting } from "@/components/auth/greeting-context";

// Guard for the auth screens (APP-1 §4). An already-authenticated user visiting /login,
// /register, etc. is sent on to /app (or back to wherever they were headed). Reset
// password stays reachable while signed in? No — APP-1 lists all four as public-only, so
// they redirect when authenticated, consistent with "/login should redirect to /app".
export function PublicRoute() {
  const { status } = useAuth();
  const { playing } = useGreeting();
  const location = useLocation();
  const from = (location.state as { from?: Location } | null)?.from?.pathname;

  if (status === "loading") return <AuthLoadingState />;
  // Defer the post-login redirect while the "Docura Says Hello" greeting is playing, so the login
  // page (and its grid) stays mounted; the greeting navigates to the destination when it ends.
  if (status === "authenticated" && !playing) return <Navigate to={from ?? "/app"} replace />;
  return <Outlet />;
}
