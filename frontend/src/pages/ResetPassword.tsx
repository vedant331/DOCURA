import { useMemo, useState, type FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { AuthButton } from "@/components/auth/AuthButton";
import { AuthError } from "@/components/auth/AuthError";
import { AuthField } from "@/components/auth/AuthField";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { ApiError, confirmPasswordReset } from "@/lib/api";
import { required } from "@/lib/validation";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const token = useMemo(() => params.get("token") ?? "", [params]);

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{ password?: string; confirm?: string }>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  // A token that the backend rejects (invalid/expired/spent) flips this on, so we show a
  // dedicated recovery-again state rather than a bare error.
  const [tokenInvalid, setTokenInvalid] = useState(!token);

  const validate = () => {
    const errors: typeof fieldErrors = {};
    if (!required(password)) errors.password = "Choose a new sequence key.";
    if (confirm !== password) errors.confirm = "The two keys do not match.";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!validate()) return;
    setSubmitting(true);
    try {
      await confirmPasswordReset(token, password);
      setDone(true);
    } catch (err) {
      if (err instanceof ApiError && [400, 404, 410, 422].includes(err.status)) {
        setTokenInvalid(true);
      } else {
        setFormError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const backToLogin = (
    <Link to="/login" className="text-muted-foreground hover:text-foreground">
      Return to Sign In
    </Link>
  );

  if (done) {
    return (
      <AuthLayout systemId="System Node · Reset Complete" title={<>KEY<br />RESET</>} footer={backToLogin}>
        <div role="status" className="animate-fade-in border border-border bg-surface/60 p-6">
          <p className="label-system mb-3">Sequence Key Updated</p>
          <p className="text-sm leading-relaxed text-muted-foreground">
            Your sequence key has been reset and existing sessions were ended. Sign in with the new
            key to continue.
          </p>
        </div>
      </AuthLayout>
    );
  }

  if (tokenInvalid) {
    return (
      <AuthLayout systemId="System Node · Recovery" title={<>LINK<br />EXPIRED</>} footer={backToLogin}>
        <div role="alert" className="animate-fade-in border border-destructive/40 bg-destructive/10 p-6">
          <p className="label-system mb-3 text-destructive">Invalid or Expired Link</p>
          <p className="text-sm leading-relaxed text-muted-foreground">
            This recovery link is no longer valid. Request a fresh one to reset your sequence key.
          </p>
          <Link
            to="/forgot-password"
            className="mt-4 inline-block font-mono text-[11px] uppercase tracking-[0.2em] text-foreground underline underline-offset-4"
          >
            Request a new link
          </Link>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      systemId="System Node · Reset Key"
      title={<>SET NEW<br />KEY</>}
      footer={backToLogin}
    >
      <form onSubmit={onSubmit} noValidate aria-label="Reset password">
        <AuthError message={formError} />
        <AuthField
          label="New Sequence Key"
          type="password"
          name="password"
          autoComplete="new-password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={fieldErrors.password}
          disabled={submitting}
          autoFocus
        />
        <AuthField
          label="Confirm Sequence Key"
          type="password"
          name="confirm-password"
          autoComplete="new-password"
          placeholder="••••••••"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          error={fieldErrors.confirm}
          disabled={submitting}
        />
        <AuthButton loading={submitting} loadingLabel="Resetting">
          Reset Sequence Key
        </AuthButton>
      </form>
    </AuthLayout>
  );
}
