import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import * as api from "@/lib/api";
import { useAuth } from "@/auth/AuthContext";
import { useAsync } from "@/hooks/useAsync";
import { formatDateTime } from "@/lib/format";
import { PageHeader } from "@/components/app/PageHeader";
import { Button } from "@/components/ui/button";
import { ConfirmationDialog } from "@/components/system/ConfirmationDialog";
import { ErrorState, LoadingState, NotConnected } from "@/components/system/states";

// /app/settings — account, security, and data controls (§16). Every control maps to a
// real backend capability (account info, active sessions, sign-out-everywhere) or is an
// honest seam where none exists (password change has only the reset-by-email flow;
// account deletion has no endpoint). No sharing controls — sharing is not an MVP feature.
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="border border-border bg-surface/30">
      <h2 className="border-b border-border px-4 py-3 text-sm font-semibold text-foreground">{title}</h2>
      <div className="space-y-4 p-4">{children}</div>
    </section>
  );
}

export default function SettingsPage() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const sessions = useAsync(() => api.listAuthSessions());
  const [revoking, setRevoking] = useState(false);

  return (
    <>
      <PageHeader
        eyebrow="Settings"
        title="Settings"
        description="Your account, active sessions, and data controls."
      />

      <div className="space-y-6">
        <Section title="Account">
          <dl className="grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="label-system">Email</dt>
              <dd className="mt-1 font-mono text-sm text-foreground">{user?.email ?? "—"}</dd>
            </div>
            <div>
              <dt className="label-system">Account created</dt>
              <dd className="mt-1 text-sm text-foreground">
                {user?.created_at ? formatDateTime(user.created_at) : "—"}
              </dd>
            </div>
          </dl>
        </Section>

        <Section title="Security">
          <div>
            <p className="label-system mb-2">Active sessions</p>
            {sessions.status === "loading" ? (
              <LoadingState label="Loading sessions" />
            ) : sessions.status === "error" ? (
              <ErrorState message={sessions.error ?? undefined} onRetry={sessions.reload} />
            ) : (
              <ul className="divide-y divide-border border border-border">
                {(sessions.data?.sessions ?? []).map((s) => (
                  <li key={s.id} className="flex flex-wrap items-center justify-between gap-2 px-3 py-2 text-sm">
                    <span className="font-mono text-[11px] text-muted-foreground">
                      {s.id.slice(0, 8)} · last used {formatDateTime(s.last_used_at)}
                    </span>
                    {s.current ? (
                      <span className="font-mono text-[10px] uppercase tracking-[0.15em] text-emerald-300">
                        this device
                      </span>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Button variant="outline" onClick={() => setRevoking(true)}>
              Sign out everywhere
            </Button>
            <Button asChild variant="ghost">
              <Link to="/forgot-password">Change password</Link>
            </Button>
          </div>
          <NotConnected
            title="Password change"
            description="Changing your password uses the email reset flow — there is no in-app password-change endpoint. Signing out everywhere revokes all sessions, including this one."
          />
        </Section>

        <Section title="Privacy & data">
          <div>
            <p className="text-sm text-foreground">Delete documents</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Remove individual documents (and anything extracted from them) from your vault.
            </p>
            <Button asChild variant="outline" className="mt-2">
              <Link to="/app/documents">Open document vault</Link>
            </Button>
          </div>
          <div className="border-t border-border pt-4">
            <p className="text-sm text-foreground">Delete account</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Permanently deleting your account and all data is a destructive action.
            </p>
            <NotConnected
              className="mt-2"
              title="Account deletion not yet connected"
              description="There is no account-deletion endpoint yet. When connected, it will require explicit confirmation and cannot be undone."
            />
          </div>
        </Section>
      </div>

      <ConfirmationDialog
        open={revoking}
        onOpenChange={setRevoking}
        title="Sign out of every device?"
        description="This revokes all active sessions for your account, including this one. You'll need to sign in again."
        confirmLabel="Sign out everywhere"
        destructive
        onConfirm={async () => {
          await api.revokeAllAuthSessions();
          await signOut();
          navigate("/login", { replace: true });
        }}
      />
    </>
  );
}
