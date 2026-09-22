import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "@/auth/AuthContext";
import { AuthButton } from "@/components/auth/AuthButton";
import { AuthError } from "@/components/auth/AuthError";
import { AuthField } from "@/components/auth/AuthField";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { LoginGreeting } from "@/components/auth/LoginGreeting";
import { useGreeting } from "@/components/auth/greeting-context";
import { ApiError } from "@/lib/api";
import { isEmail, required } from "@/lib/validation";

export default function Login() {
  const { signIn } = useAuth();
  const greeting = useGreeting();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: Location } | null)?.from?.pathname ?? "/overview";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const validate = () => {
    const errors: { email?: string; password?: string } = {};
    if (!required(email)) errors.email = "Enter your user identity.";
    else if (!isEmail(email)) errors.email = "That does not look like an email address.";
    if (!required(password)) errors.password = "Enter your sequence key.";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!validate()) return;
    setSubmitting(true);
    try {
      await signIn(email.trim(), password);
      // Authentication succeeded — play the greeting (PublicRoute defers its redirect while it
      // plays); it navigates to `from` when it completes. We do NOT navigate immediately here.
      greeting.play();
    } catch (err) {
      // Invalid credentials (401) and backend/transport errors both land here; the
      // backend's `detail` is already human-readable and safe to show.
      const message =
        err instanceof ApiError
          ? err.status === 401
            ? "Those credentials were not accepted. Check them and try again."
            : err.message
          : "Something went wrong. Try again.";
      setFormError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
    <AuthLayout
      dimmed={greeting.playing}
      systemId="System Node · Sign In"
      title={
        <>
          NEURAL
          <br />
          ACCESS
        </>
      }
      footer={
        <>
          <Link to="/forgot-password" className="text-muted-foreground hover:text-foreground">
            Encrypted Recovery
          </Link>
          <Link to="/register" className="text-muted-foreground hover:text-foreground">
            New Archive
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} noValidate aria-label="Sign in">
        <AuthError message={formError} />
        <AuthField
          label="User Identity"
          type="email"
          name="email"
          autoComplete="username"
          placeholder="id@domain"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={fieldErrors.email}
          disabled={submitting}
          autoFocus
        />
        <AuthField
          label="Sequence Key"
          type="password"
          name="password"
          autoComplete="current-password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={fieldErrors.password}
          disabled={submitting}
        />
        <AuthButton loading={submitting} loadingLabel="Initializing">
          Initialize Stream
        </AuthButton>
      </form>
    </AuthLayout>
    {greeting.playing ? (
      <LoginGreeting
        onDone={() => {
          greeting.stop();
          navigate(from, { replace: true });
        }}
      />
    ) : null}
    </>
  );
}
