import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "@/auth/AuthContext";
import { AuthLoadingState } from "@/components/auth/AuthLoadingState";

// Guard for /app/* (APP-1 §4). While the session is being revalidated, wait — never
// bounce an authenticated user to /login on a refresh. Unauthenticated → /login, keeping
// the attempted location so we can return there after signing in.
export function ProtectedRoute() {
  const { status } = useAuth();
  const location = useLocation();

  if (status === "loading") return <AuthLoadingState />;
  if (status === "unauthenticated") {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return <Outlet />;
}
