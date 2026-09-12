import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "@/auth/AuthContext";
import { AuthButton } from "@/components/auth/AuthButton";
import { AuthError } from "@/components/auth/AuthError";
import { AuthField } from "@/components/auth/AuthField";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { ApiError } from "@/lib/api";
import { isEmail, required } from "@/lib/validation";

export default function Register() {
  const { signUp } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{
    email?: string;
    password?: string;
    confirm?: string;
  }>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const validate = () => {
    const errors: typeof fieldErrors = {};
    if (!required(email)) errors.email = "Enter an email address.";
    else if (!isEmail(email)) errors.email = "That does not look like an email address.";
    if (!required(password)) errors.password = "Choose a sequence key.";
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
      // Backend opens no session on register, so signUp registers then signs in.
      await signUp(email.trim(), password);
      navigate("/app", { replace: true });
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Something went wrong. Try again.";
      setFormError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout
      systemId="System Node · New Archive"
      title={
        <>
          CREATE
          <br />
          IDENTITY
        </>
      }
      footer={
        <Link to="/login" className="text-muted-foreground hover:text-foreground">
          Return to Sign In
        </Link>
      }
    >
      <form onSubmit={onSubmit} noValidate aria-label="Create account">
        <AuthError message={formError} />
        <AuthField
          label="Email"
          type="email"
          name="email"
          autoComplete="email"
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
          autoComplete="new-password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={fieldErrors.password}
          disabled={submitting}
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
        <AuthButton loading={submitting} loadingLabel="Creating">
          Create Identity
        </AuthButton>
      </form>
    </AuthLayout>
  );
}
