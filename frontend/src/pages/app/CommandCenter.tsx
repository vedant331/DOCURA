import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, UploadCloud } from "lucide-react";

import * as api from "@/lib/api";
import { useAsync } from "@/hooks/useAsync";
import { useAuth } from "@/auth/AuthContext";
import { PageHeader } from "@/components/app/PageHeader";
import { Button } from "@/components/ui/button";
import { CommandCenter } from "@/components/command/CommandCenter";
import { UploadDialog } from "@/components/documents/UploadDialog";
import { StatusBadge, sessionStateToStatus } from "@/components/system/StatusBadge";
import { ErrorState, LoadingState } from "@/components/system/states";

// /app — the DOCURA command center (§5/§35). Primary post-login surface; adapts to real
// document state.
export default function CommandCenterPage() {
  const { user } = useAuth();
  const docs = useAsync(() => api.listDocuments());
  const limits = useAsync(() => api.getUploadLimits());
  const sessions = useAsync(() => api.listFormSessions());
  const [uploadOpen, setUploadOpen] = useState(false);

  const formSessions = sessions.data?.sessions ?? [];

  return (
    <>
      <PageHeader
        eyebrow="Command Center"
        title="Welcome back"
        description={
          <>
            Signed in as <span className="font-mono text-foreground">{user?.email ?? "unknown"}</span>. Start with your
            documents, or jump to any section from the sidebar.
          </>
        }
        actions={
          <Button variant="primary" onClick={() => setUploadOpen(true)}>
            <UploadCloud className="size-4" aria-hidden /> Upload
          </Button>
        }
      />

      {docs.status === "loading" ? (
        <LoadingState label="Loading your vault" />
      ) : docs.status === "error" ? (
        <ErrorState message={docs.error ?? undefined} onRetry={docs.reload} />
      ) : (
        <CommandCenter documents={docs.data?.documents ?? []} onUpload={() => setUploadOpen(true)} />
      )}

      {formSessions.length > 0 ? (
        <section aria-labelledby="form-sessions" className="mt-6">
          <h2 id="form-sessions" className="label-system mb-3">Form sessions</h2>
          <ul className="divide-y divide-border border border-border bg-surface/30">
            {formSessions.map((s) => (
              <li key={s.id}>
                <Link
                  to={`/app/forms/${s.id}`}
                  className="flex items-center justify-between gap-3 px-4 py-3 text-sm transition-colors hover:bg-surface/60"
                >
                  <span className="flex items-center gap-3">
                    <StatusBadge status={sessionStateToStatus(s.state)} label={s.state.replace("_", " ")} />
                    <span className="font-mono text-[11px] text-muted-foreground">{s.id.slice(0, 8)}</span>
                  </span>
                  <ArrowRight className="size-4 text-muted-foreground" aria-hidden />
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <UploadDialog
        open={uploadOpen}
        onOpenChange={setUploadOpen}
        limits={limits.data}
        onUploaded={docs.reload}
      />
    </>
  );
}
