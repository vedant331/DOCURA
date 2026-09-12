import { Button, type ButtonProps } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// The Mercury primary action (APP-1 §7/§10). Delegates the loading spinner/disabled
// behaviour to the base Button; this wrapper just fixes the submit semantics and width.
export function AuthButton({
  loading = false,
  loadingLabel = "Working",
  children,
  className,
  ...props
}: ButtonProps & { loading?: boolean; loadingLabel?: string }) {
  return (
    <Button
      type="submit"
      variant="primary"
      className={cn("mt-4 w-full", className)}
      loading={loading}
      loadingLabel={loadingLabel}
      {...props}
    >
      {children}
    </Button>
  );
}
