import { useState } from "react";
import { Power } from "lucide-react";

import * as api from "@/lib/api";
import { useAsync } from "@/hooks/useAsync";
import { Button } from "@/components/ui/button";
import { ActivityTimeline } from "@/components/activity/ActivityTimeline";
import { ConfirmationDialog } from "@/components/system/ConfirmationDialog";
import { EmptyState, LoadingState, NotConnected } from "@/components/system/states";
import { useFormSession } from "@/pages/app/forms/FormSessionLayout";

// /app/forms/:sessionId — the session entry view (§17). Real lifecycle (state, hand-back,
// stop) and the real per-session action log. Field detection / readiness / matching are
// produced in the extension's isolated world and are not bridged to the web backend, so
// that detail is an honest seam (see the Readiness tab).
export default function FormSessionOverview() {
  const { session, reload } = useFormSession();
  const actions = useAsync(() => api.getFormSessionActions(session.id), [session.id]);
  const [stopping, setStopping] = useState(false);
  const [handingBack, setHandingBack] = useState(false);
  const active = session.state === "active";

  const handBack = async () => {
    setHandingBack(true);
    try {
      await api.handBackFormSession(session.id);
      reload();
    } finally {
      setHandingBack(false);
    }
  };

  return (
    <div className="space-y-6">
      {active ? (
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="primary" onClick={handBack} loading={handingBack} loadingLabel="Handing back">
            Hand back to me
          </Button>
          <Button variant="destructive" onClick={() => setStopping(true)}>
            <Power className="size-4" aria-hidden /> Stop session
          </Button>
        </div>
      ) : null}

      <NotConnected
        title="Field detection lives in the extension"
        description="What fields were detected, what can be filled, and what needs you are computed in the browser extension's isolated world and are not sent to the web backend. Use the Readiness tab for what the web app can show."
      />

      <section aria-labelledby="session-actions">
        <h3 id="session-actions" className="mb-3 text-sm font-semibold text-foreground">
          Actions in this session
        </h3>
        {actions.status === "loading" ? (
          <LoadingState label="Loading actions" />
        ) : (actions.data?.actions.length ?? 0) === 0 ? (
          <EmptyState
            title="No actions recorded"
            description="Fills, selections, attachments, questions, and approvals appear here as they happen."
          />
        ) : (
          <ActivityTimeline actions={actions.data!.actions} />
        )}
      </section>

      <ConfirmationDialog
        open={stopping}
        onOpenChange={setStopping}
        title="Stop this form session?"
        description="DOCURA will stop working on this form. The audit trail is kept. This cannot be resumed."
        confirmLabel="Stop session"
        destructive
        onConfirm={async () => {
          await api.stopFormSession(session.id);
          reload();
        }}
      />
    </div>
  );
}
