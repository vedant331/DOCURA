import * as api from "@/lib/api";
import type { FormActionResponse } from "@/lib/api";
import { useAsync } from "@/hooks/useAsync";
import { PageHeader } from "@/components/app/PageHeader";
import { ActivityTimeline } from "@/components/activity/ActivityTimeline";
import { EmptyState, ErrorState, LoadingState, NotConnected } from "@/components/system/states";

// /app/activity — user-viewable audit (§15). The backend records per-form-session actions
// (fill/select/attach/ask/approval/hand-back/stop/…); we gather them across every session
// and present one read-only, newest-first timeline (FR-AUD-004/005). Actions carry no
// third-party form content. Document-level events (upload/processing/extraction) are not
// exposed by an audit endpoint yet — stated honestly rather than faked.
async function loadActivity(): Promise<FormActionResponse[]> {
  const { sessions } = await api.listFormSessions();
  const perSession = await Promise.all(
    sessions.map((s) => api.getFormSessionActions(s.id).then((r) => r.actions)),
  );
  return perSession
    .flat()
    .sort((a, b) => b.created_at.localeCompare(a.created_at));
}

export default function ActivityPage() {
  const activity = useAsync(loadActivity);

  return (
    <>
      <PageHeader
        eyebrow="Activity"
        title="Activity"
        description="A read-only history of DOCURA's actions on your behalf during form sessions. This record cannot be edited."
      />

      {activity.status === "loading" ? (
        <LoadingState label="Loading activity" />
      ) : activity.status === "error" ? (
        <ErrorState message={activity.error ?? undefined} onRetry={activity.reload} />
      ) : (activity.data?.length ?? 0) === 0 ? (
        <div className="space-y-4">
          <EmptyState
            title="No activity yet"
            description="Actions DOCURA takes inside a form session appear here. Start a form session from the browser extension to see its audit trail."
          />
          <NotConnected
            title="Document events not in this log"
            description="Uploads, processing, and extraction are tracked by the backend but are not exposed through an audit endpoint yet, so they are not listed here."
          />
        </div>
      ) : (
        <ActivityTimeline actions={activity.data!} />
      )}
    </>
  );
}
