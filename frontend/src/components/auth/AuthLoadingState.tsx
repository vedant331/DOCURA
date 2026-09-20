import { BlinkingSquares } from "@/components/ui/blinking-squares";

// Full-screen loading state in the DOCURA language (APP-1 §10). Shown while the auth
// session is being revalidated on first load, so guards never flash the login screen at
// an already-authenticated user.
export function AuthLoadingState({ label = "Establishing secure session" }: { label?: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="relative flex min-h-screen w-full items-center justify-center bg-bg"
    >
      <BlinkingSquares />
      <div className="relative z-10 flex flex-col items-center gap-4">
        <span className="label-system">DOCURA</span>
        <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-[0.2em] text-muted-foreground">
          <span className="inline-block size-2 animate-pulse rounded-full bg-mercury" aria-hidden />
          {label}
        </div>
      </div>
    </div>
  );
}
