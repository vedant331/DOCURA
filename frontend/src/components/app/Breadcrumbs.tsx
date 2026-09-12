import { Fragment } from "react";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";

export interface Crumb {
  label: string;
  to?: string;
}

// Breadcrumb trail for nested surfaces (document detail, form session sub-pages).
export function Breadcrumbs({ items }: { items: Crumb[] }) {
  if (items.length === 0) return null;
  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex flex-wrap items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
        {items.map((item, i) => {
          const last = i === items.length - 1;
          return (
            <Fragment key={`${item.label}-${i}`}>
              <li>
                {item.to && !last ? (
                  <Link to={item.to} className="transition-colors hover:text-foreground">
                    {item.label}
                  </Link>
                ) : (
                  <span aria-current={last ? "page" : undefined} className={last ? "text-foreground" : undefined}>
                    {item.label}
                  </span>
                )}
              </li>
              {!last ? <ChevronRight className="size-3" aria-hidden /> : null}
            </Fragment>
          );
        })}
      </ol>
    </nav>
  );
}
