import { cn } from "@/lib/utils";

// DOCURA wordmark + system status dot, reused in the sidebar and mobile drawer header.
export function Brand({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      <span
        aria-hidden
        className="inline-block size-2 rounded-full bg-mercury [box-shadow:0_0_10px_hsl(var(--mercury))]"
      />
      <span className="text-lg font-extrabold tracking-tight text-foreground">DOCURA</span>
      <span className="label-system ml-auto">v0.1</span>
    </div>
  );
}
