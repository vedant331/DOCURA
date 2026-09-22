import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/app/AppShell";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { PublicRoute } from "@/components/PublicRoute";
import { ClickSpark } from "@/components/ui/click-spark";
import ForgotPassword from "@/pages/ForgotPassword";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import ResetPassword from "@/pages/ResetPassword";
import OverviewPage from "@/pages/app/Overview";
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
    <>
      {/* One global spark overlay for the whole app — DOCURA lime, subtle, pointer-safe. */}
      <ClickSpark sparkColor="#B8F35A" sparkSize={6} sparkRadius={12} sparkCount={6} duration={300} easing="ease-out" extraScale={0.85} />
    <Routes>
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          {/* Overview — the informational product page and post-login landing surface. */}
          <Route path="/overview" element={<OverviewPage />} />
          {/* Ask — the DOCURA AI chat workspace (reuses the existing CommandCenter). */}
          <Route path="/ask" element={<CommandCenterPage />} />

          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/documents/:documentId" element={<DocumentDetailPage />} />
          <Route path="/record" element={<MyRecordPage />} />
          <Route path="/activity" element={<ActivityPage />} />
          <Route path="/settings" element={<SettingsPage />} />

          {/* Form-session surfaces (§17/§18/§26/§24), nested so the session loads once. */}
          <Route path="/forms/:sessionId" element={<FormSessionLayout />}>
            <Route index element={<FormSessionOverview />} />
            <Route path="readiness" element={<ReadinessPage />} />
            <Route path="review" element={<ReviewPage />} />
            <Route path="approval" element={<ApprovalPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="/" element={<Navigate to="/overview" replace />} />
      <Route path="*" element={<Navigate to="/overview" replace />} />
    </Routes>
    </>
  );
}
