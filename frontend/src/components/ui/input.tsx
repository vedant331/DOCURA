import * as React from "react";

import { cn } from "@/lib/utils";

// DOCURA input: transparent field on a thin under-border that lights metallic on focus
// (Mercury reference). No boxy shadcn card look.
const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      ref={ref}
      className={cn(
        "w-full border-0 border-b border-border bg-transparent px-0 py-3 text-lg text-foreground",
        "placeholder:text-muted-foreground/60 transition-colors duration-300",
        "focus-visible:border-accent focus-visible:outline-none",
        "disabled:cursor-not-allowed disabled:opacity-50",
        "aria-[invalid=true]:border-destructive",
        className,
      )}
      {...props}
    />
  ),
);
Input.displayName = "Input";

export { Input };
