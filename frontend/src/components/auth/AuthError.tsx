import { AlertTriangle } from "lucide-react";

// Backend / submit-level error, styled into the Mercury language rather than a browser
// alert (APP-1 §10). role="alert" so assistive tech announces it; used for invalid
// credentials, backend errors, and transport failures alike (the message is chosen by
// the caller from ApiError.detail).
export function AuthError({ message }: { message?: string | null }) {
  if (!message) return null;
  return (
    <div
      role="alert"
      className="mb-6 flex items-start gap-3 border border-destructive/40 bg-destructive/10 px-4 py-3"
    >
      <AlertTriangle className="mt-0.5 size-4 shrink-0 text-destructive" aria-hidden />
      <p className="font-mono text-[11px] leading-relaxed tracking-wide text-destructive">
        {message}
      </p>
    </div>
  );
}
