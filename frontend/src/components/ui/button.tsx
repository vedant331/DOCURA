import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";

// shadcn Button, re-skinned to the DOCURA system (APP-1 §6/§7): metallic-white primary,
// mono uppercase system labels, thin borders, restrained motion. Not the default look.
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap font-mono text-xs font-bold uppercase tracking-system transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-bg disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        // High-contrast metallic primary action.
        primary:
          "bg-primary text-primary-foreground hover:tracking-[0.3em] hover:brightness-110 active:brightness-95",
        outline:
          "border border-border bg-transparent text-foreground hover:border-mercury/40 hover:bg-surface",
        ghost: "bg-transparent text-muted-foreground hover:text-foreground hover:bg-surface",
        destructive:
          "bg-destructive text-destructive-foreground hover:brightness-110",
        link: "text-muted-foreground underline-offset-4 hover:text-foreground hover:underline tracking-normal normal-case font-sans",
      },
      size: {
        default: "h-12 px-6 py-2",
        sm: "h-9 px-4",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: { variant: "primary", size: "default" },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  loadingLabel?: string;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, loading = false, loadingLabel, children, disabled, ...props }, ref) => {
    // asChild + loading is ambiguous (Slot needs a single child), so loading is ignored
    // when asChild is set — callers that need a spinner use a plain button.
    if (asChild) {
      return <Slot className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props}>{children}</Slot>;
    }
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || loading}
        aria-busy={loading || undefined}
        {...props}
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin" aria-hidden />
            {loadingLabel ?? children}
          </>
        ) : (
          children
        )}
      </button>
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
