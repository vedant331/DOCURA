import { useState } from "react";

import * as api from "@/lib/api";
import { HandBackPanel } from "@/components/forms/HandBackPanel";
import { NotConnected } from "@/components/system/states";
import { useFormSession } from "@/pages/app/forms/FormSessionLayout";

// /app/forms/:sessionId/review — the final review & hand-back (§26/§27). DOCURA never
// submits: hand-back returns control to the user, who submits the form themselves. Field-
// level review (per-field values, sources, blockers, attachments) is produced in the
// extension and not bridged to the web backend, so blockers are "not known here" rather
// than falsely reported as zero — but the hand-back lifecycle itself is real.
export default function ReviewPage() {
  const { session, reload } = useFormSession();
  const [handingBack, setHandingBack] = useState(false);
  const handedBack = session.state !== "active";

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
      <NotConnected
        title="Field-level review lives in the extension"
        description="Per-field values, sources, confidence, attachments, and outstanding blockers are assembled on the form by the extension. The web backend does not store them, so the web app shows the session state and the hand-back, not a per-field summary."
      />

      <HandBackPanel
        outstandingCount={handedBack ? 0 : null}
        handedBack={handedBack}
        onHandBack={handBack}
        handingBack={handingBack}
      />
    </div>
  );
}
