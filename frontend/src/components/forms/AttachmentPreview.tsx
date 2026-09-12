import { ArrowRight, FileCheck2, ShieldCheck } from "lucide-react";

// Attachment preview (§23). Shows the original vs the prepared copy, the target field, and
// the constraints, and states plainly that the original is unchanged (BR-013). This is the
// exact-file preview target M7 produces; the prepared copy is a derived artefact, never a
// modification of the source.
export function AttachmentPreview({
  originalName,
  preparedName,
  targetField,
  format,
  size,
  constraints,
}: {
  originalName: string;
  preparedName?: string | null;
  targetField: string;
  format?: string;
  size?: string;
  constraints?: string;
}) {
  return (
    <section className="border border-border bg-surface/30 p-4">
      <div className="flex items-center gap-2">
        <FileCheck2 className="size-4 text-mercury" aria-hidden />
        <p className="text-sm font-semibold text-foreground">Attachment preview</p>
      </div>

      <div className="mt-3 grid items-center gap-3 sm:grid-cols-[1fr_auto_1fr]">
        <div className="border border-border bg-surface/50 p-3">
          <p className="label-system">Original</p>
          <p className="mt-1 truncate text-sm text-foreground">{originalName}</p>
        </div>
        <ArrowRight className="mx-auto hidden size-4 text-muted-foreground sm:block" aria-hidden />
        <div className="border border-border bg-surface/50 p-3">
          <p className="label-system">Prepared copy</p>
          <p className="mt-1 truncate text-sm text-foreground">{preparedName ?? "— (original meets constraints)"}</p>
        </div>
      </div>

      <dl className="mt-3 grid grid-cols-2 gap-3 font-mono text-[11px] text-muted-foreground sm:grid-cols-4">
        <div><dt className="label-system">Target</dt><dd className="mt-1 text-foreground">{targetField}</dd></div>
        {format ? <div><dt className="label-system">Format</dt><dd className="mt-1 text-foreground">{format}</dd></div> : null}
        {size ? <div><dt className="label-system">Size</dt><dd className="mt-1 text-foreground">{size}</dd></div> : null}
        {constraints ? <div><dt className="label-system">Constraints</dt><dd className="mt-1 text-foreground">{constraints}</dd></div> : null}
      </dl>

      <p className="mt-3 inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.15em] text-emerald-300">
        <ShieldCheck className="size-3" aria-hidden />
        The original document remains unchanged.
      </p>
    </section>
  );
}
