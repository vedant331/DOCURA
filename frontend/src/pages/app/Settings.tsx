import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import * as api from "@/lib/api";
import { useAuth } from "@/auth/AuthContext";
import { useAsync } from "@/hooks/useAsync";
import { formatDateTime } from "@/lib/format";
import { PageHeader } from "@/components/app/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
  const [deleting, setDeleting] = useState(false);
  const [confirmEmail, setConfirmEmail] = useState("");

  const email = user?.email ?? "";
  const canDelete = confirmEmail.trim().toLowerCase() === email.toLowerCase() && email.length > 0;

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
            <Button variant="primary" onClick={() => setRevoking(true)}>
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
            <Button asChild variant="primary" className="mt-2">
              <Link to="/documents">Open document vault</Link>
            </Button>
          </div>
          <div className="border-t border-border pt-4">
            <p className="text-sm text-foreground">Delete account</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Permanently delete your account and all data — every document and anything
              extracted from it, your record, your sessions, and your form-session history. This
              cannot be undone.
            </p>
            <Button variant="destructive" className="mt-2" onClick={() => setDeleting(true)}>
              Delete account
            </Button>
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

      <ConfirmationDialog
        open={deleting}
        onOpenChange={(o) => {
          setDeleting(o);
          if (!o) setConfirmEmail("");
        }}
        title="Delete your account?"
        description={
          <>
            This permanently deletes your account and everything in it — documents, extracted
            information, your record, sessions, and form-session history. It cannot be undone. Type
            your email <span className="font-mono text-foreground">{email}</span> to confirm.
          </>
        }
        confirmLabel="Delete account"
        destructive
        confirmDisabled={!canDelete}
        onConfirm={async () => {
          await api.deleteAccount(confirmEmail.trim());
          await signOut(); // this session's token is already invalidated server-side
          navigate("/login", { replace: true });
        }}
      >
        <div className="space-y-1.5">
          <label htmlFor="confirm-email" className="label-system">
            Confirm your email
          </label>
          <Input
            id="confirm-email"
            type="email"
            autoComplete="off"
            value={confirmEmail}
            placeholder={email}
            onChange={(e) => setConfirmEmail(e.target.value)}
          />
        </div>
      </ConfirmationDialog>
    </>
  );
}
