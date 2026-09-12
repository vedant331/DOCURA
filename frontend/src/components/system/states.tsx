import { type ReactNode } from "react";
import { AlertTriangle, Inbox, Loader2, PlugZap } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// Shared page/section states (§29). Each is accessible (role + live region where it
// conveys a transient status) and never leaves a blank screen.

export function LoadingState({ label = "Loading", className }: { label?: string; className?: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn("flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground", className)}
    >
      <Loader2 className="size-6 animate-spin" aria-hidden />
      <span className="font-mono text-xs uppercase tracking-[0.2em]">{label}</span>
    </div>
  );
}

export function ErrorState({
  message = "Something went wrong.",
  onRetry,
  className,
}: {
  message?: string;
  onRetry?: () => void;
  className?: string;
}) {
  return (
    <div
      role="alert"
      className={cn(
        "flex flex-col items-center justify-center gap-3 border border-destructive/40 bg-destructive/10 px-6 py-12 text-center",
        className,
      )}
    >
      <AlertTriangle className="size-6 text-destructive" aria-hidden />
      <p className="max-w-md text-sm text-foreground">{message}</p>
      {onRetry ? (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try again
        </Button>
      ) : null}
    </div>
  );
}

export function EmptyState({
  title,
  description,
  icon,
  action,
  className,
}: {
  title: string;
  description?: ReactNode;
  icon?: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-4 border border-dashed border-border bg-surface/30 px-6 py-16 text-center",
        className,
      )}
    >
      <div className="text-muted-foreground" aria-hidden>
        {icon ?? <Inbox className="size-8" />}
      </div>
      <div className="space-y-1">
        <p className="text-base font-semibold text-foreground">{title}</p>
        {description ? <div className="mx-auto max-w-md text-sm text-muted-foreground">{description}</div> : null}
      </div>
      {action}
    </div>
  );
}

// The honest "capability has no backend yet" seam (§6/§33). Used wherever the UI is
// deliberately ahead of the backend (assistant, correction persistence, extension-side
// data). It never fabricates data or success.
export function NotConnected({
  title = "Not yet connected",
  description,
  className,
}: {
  title?: string;
  description?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex items-start gap-3 border border-border bg-surface/40 px-4 py-3 text-sm text-muted-foreground",
        className,
      )}
    >
      <PlugZap className="mt-0.5 size-4 shrink-0 text-muted-foreground" aria-hidden />
      <div>
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted-foreground">{title}</p>
        {description ? <p className="mt-1 leading-relaxed">{description}</p> : null}
      </div>
    </div>
  );
}
