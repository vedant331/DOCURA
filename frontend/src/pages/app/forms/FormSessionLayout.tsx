import { NavLink, Outlet, useOutletContext, useParams } from "react-router-dom";

import * as api from "@/lib/api";
import type { FormSessionResponse } from "@/lib/api";
import { useAsync } from "@/hooks/useAsync";
import { PageHeader } from "@/components/app/PageHeader";
import { FormSessionHeader } from "@/components/forms/FormSessionHeader";
import { ErrorState, LoadingState } from "@/components/system/states";
import { cn } from "@/lib/utils";

// Shared shell for the form-session surfaces (§17). Fetches the real session once and
// renders the header + sub-navigation; each sub-page (entry, readiness, review, approval)
// renders into the Outlet and reads the session via context.
export interface FormSessionContext {
  session: FormSessionResponse;
  reload: () => void;
}

export function useFormSession() {
  return useOutletContext<FormSessionContext>();
}

const SUBNAV = [
  { to: ".", label: "Session", end: true },
  { to: "readiness", label: "Readiness", end: false },
  { to: "review", label: "Review", end: false },
  { to: "approval", label: "Approval", end: false },
];

export default function FormSessionLayout() {
  const { sessionId = "" } = useParams();
  const session = useAsync(() => api.getFormSession(sessionId), [sessionId]);

  return (
    <>
      <PageHeader
        breadcrumbs={[{ label: "Form session" }, { label: sessionId.slice(0, 8) }]}
        eyebrow="Form session"
        title="Form session"
        description="The web-side view of a DOCURA form session: its lifecycle, what it needs from you, and the hand-back to your own review."
      />

      {session.status === "loading" ? (
        <LoadingState label="Loading session" />
      ) : session.status === "error" || !session.data ? (
        <ErrorState message={session.error ?? "Session not found."} onRetry={session.reload} />
      ) : (
        <div className="space-y-6">
          <FormSessionHeader session={session.data} />

          <nav aria-label="Form session sections" className="flex flex-wrap gap-1 border-b border-border">
            {SUBNAV.map((s) => (
              <NavLink
                key={s.to}
                to={s.to}
                end={s.end}
                className={({ isActive }) =>
                  cn(
                    "-mb-px border-b-2 px-3 py-2 text-sm transition-colors",
                    isActive
                      ? "border-mercury text-foreground"
                      : "border-transparent text-muted-foreground hover:text-foreground",
                  )
                }
              >
                {s.label}
              </NavLink>
            ))}
          </nav>

          <Outlet context={{ session: session.data, reload: session.reload } satisfies FormSessionContext} />
        </div>
      )}
    </>
  );
}
