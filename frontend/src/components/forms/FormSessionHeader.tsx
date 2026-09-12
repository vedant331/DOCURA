import type { FormSessionResponse } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { StatusBadge, sessionStateToStatus } from "@/components/system/StatusBadge";

// Header for a form session (§17), built from real FormSessionResponse lifecycle data.
export function FormSessionHeader({ session }: { session: FormSessionResponse }) {
  return (
    <div className="border border-border bg-surface/40 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="label-system">Form session</p>
          <p className="mt-1 font-mono text-sm text-foreground">{session.id}</p>
        </div>
        <StatusBadge status={sessionStateToStatus(session.state)} label={session.state.replace("_", " ")} />
      </div>
      <dl className="mt-4 grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
        <div>
          <dt className="label-system">Activated</dt>
          <dd className="mt-1 text-foreground">{formatDateTime(session.created_at)}</dd>
        </div>
        <div>
          <dt className="label-system">Ended</dt>
          <dd className="mt-1 text-foreground">{session.ended_at ? formatDateTime(session.ended_at) : "—"}</dd>
        </div>
        <div>
          <dt className="label-system">State</dt>
          <dd className="mt-1 capitalize text-foreground">{session.state.replace("_", " ")}</dd>
        </div>
      </dl>
    </div>
  );
}
