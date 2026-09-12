import { forwardRef, useId, type InputHTMLAttributes } from "react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

// One labelled field for the auth forms (APP-1 §7/§8). Mono uppercase label, the Mercury
// focus glow under the input, and an accessible per-field error wired via aria-describedby
// + aria-invalid. `label` is a real <label> bound to the input; every field is keyboard
// reachable and screen-reader labelled.
interface AuthFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string | null;
}

export const AuthField = forwardRef<HTMLInputElement, AuthFieldProps>(
  ({ label, error, id, className, ...props }, ref) => {
    const autoId = useId();
    const fieldId = id ?? autoId;
    const errorId = `${fieldId}-error`;
    return (
      <div className="group relative mb-7 transition-transform duration-300 focus-within:translate-x-2">
        <Label htmlFor={fieldId} className="mb-3">
          {label}
        </Label>
        <div className="relative">
          <Input
            id={fieldId}
            ref={ref}
            aria-invalid={error ? true : undefined}
            aria-describedby={error ? errorId : undefined}
            className={className}
            {...props}
          />
          {/* Metallic focus glow — matches the Mercury reference's .input-glow. */}
          <span
            aria-hidden
            className={cn(
              "pointer-events-none absolute bottom-0 left-0 h-0.5 w-0 bg-mercury transition-all duration-500",
              "[box-shadow:0_0_15px_hsl(var(--mercury))] group-focus-within:w-full",
            )}
          />
        </div>
        {error ? (
          <p id={errorId} role="alert" className="mt-2 font-mono text-[11px] text-destructive">
            {error}
          </p>
        ) : null}
      </div>
    );
  },
);
AuthField.displayName = "AuthField";
