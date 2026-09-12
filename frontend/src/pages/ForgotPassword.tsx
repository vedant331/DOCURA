import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { AuthButton } from "@/components/auth/AuthButton";
import { AuthError } from "@/components/auth/AuthError";
import { AuthField } from "@/components/auth/AuthField";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { ApiError, requestPasswordReset } from "@/lib/api";
import { isEmail, required } from "@/lib/validation";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [fieldError, setFieldError] = useState<string | undefined>();
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!required(email)) return setFieldError("Enter your account email.");
    if (!isEmail(email)) return setFieldError("That does not look like an email address.");
    setFieldError(undefined);
    setSubmitting(true);
    try {
      // The backend answers identically whether or not the address has an account, so
      // success here means "request processed", never "account exists".
      const res = await requestPasswordReset(email.trim());
      setDone(true);
      setFormError(null);
      void res;
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout
      systemId="System Node · Encrypted Recovery"
      title={
        <>
          RECOVER
          <br />
          ACCESS
        </>
      }
      intro={
        done
          ? undefined
          : "Enter your account email. If it matches an archive, a recovery link is dispatched to it."
      }
      footer={
        <Link to="/login" className="text-muted-foreground hover:text-foreground">
          Return to Sign In
        </Link>
      }
    >
      {done ? (
        <div role="status" className="animate-fade-in border border-border bg-surface/60 p-6">
          <p className="label-system mb-3">Request Processed</p>
          <p className="text-sm leading-relaxed text-muted-foreground">
            If that address has a DOCURA account, a reset link is on its way to it. Check your
            inbox, then return to sign in.
          </p>
        </div>
      ) : (
        <form onSubmit={onSubmit} noValidate aria-label="Request password recovery">
          <AuthError message={formError} />
          <AuthField
            label="Account Email"
            type="email"
            name="email"
            autoComplete="email"
            placeholder="id@domain"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={fieldError}
            disabled={submitting}
            autoFocus
          />
          <AuthButton loading={submitting} loadingLabel="Dispatching">
            Dispatch Recovery
          </AuthButton>
        </form>
      )}
    </AuthLayout>
  );
}
