import { type ReactNode } from "react";

import { Breadcrumbs, type Crumb } from "@/components/app/Breadcrumbs";

// Consistent page heading used across authenticated screens (§3). Optional breadcrumbs,
// a mono system eyebrow, a title, a description, and a right-aligned actions slot.
export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  breadcrumbs,
}: {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  breadcrumbs?: Crumb[];
}) {
  return (
    <header className="mb-8">
      {breadcrumbs ? <Breadcrumbs items={breadcrumbs} /> : null}
      <div className="mt-2 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          {eyebrow ? <p className="label-system mb-2">{eyebrow}</p> : null}
          <h1 className="text-2xl font-extrabold tracking-tight text-foreground sm:text-3xl">{title}</h1>
          {description ? (
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">{description}</p>
          ) : null}
        </div>
        {actions ? <div className="flex shrink-0 items-center gap-2">{actions}</div> : null}
      </div>
    </header>
  );
}
