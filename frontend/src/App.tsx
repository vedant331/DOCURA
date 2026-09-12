import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/app/AppShell";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { PublicRoute } from "@/components/PublicRoute";
import ForgotPassword from "@/pages/ForgotPassword";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import ResetPassword from "@/pages/ResetPassword";
import CommandCenterPage from "@/pages/app/CommandCenter";
import DocumentsPage from "@/pages/app/Documents";
import DocumentDetailPage from "@/pages/app/DocumentDetail";
import MyRecordPage from "@/pages/app/MyRecord";
import ActivityPage from "@/pages/app/Activity";
import SettingsPage from "@/pages/app/Settings";
import FormSessionLayout from "@/pages/app/forms/FormSessionLayout";
import FormSessionOverview from "@/pages/app/forms/FormSessionOverview";
import ReadinessPage from "@/pages/app/forms/Readiness";
import ReviewPage from "@/pages/app/forms/Review";
import ApprovalPage from "@/pages/app/forms/Approval";

// The whole route map (§2/§4). Public auth routes are only reachable when signed out
// (PublicRoute); /app/* is only reachable when signed in (ProtectedRoute). Unknown paths
// fall back to the shell, which the guard bounces to /login if unauthenticated.
export default function App() {
  return (
    <Routes>
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
      </Route>

      <Route path="/app" element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          {/* Command center — the primary post-login surface (§5/§35). */}
          <Route index element={<CommandCenterPage />} />

          <Route path="documents" element={<DocumentsPage />} />
          <Route path="documents/:documentId" element={<DocumentDetailPage />} />
          <Route path="record" element={<MyRecordPage />} />
          <Route path="activity" element={<ActivityPage />} />
          <Route path="settings" element={<SettingsPage />} />

          {/* Form-session surfaces (§17/§18/§26/§24), nested so the session loads once. */}
          <Route path="forms/:sessionId" element={<FormSessionLayout />}>
            <Route index element={<FormSessionOverview />} />
            <Route path="readiness" element={<ReadinessPage />} />
            <Route path="review" element={<ReviewPage />} />
            <Route path="approval" element={<ApprovalPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="/" element={<Navigate to="/app" replace />} />
      <Route path="*" element={<Navigate to="/app" replace />} />
    </Routes>
  );
}
