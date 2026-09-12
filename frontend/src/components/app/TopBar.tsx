import { useLocation } from "react-router-dom";

import { MobileNavigation } from "@/components/app/MobileNavigation";
import { UserMenu } from "@/components/app/UserMenu";
import { titleForPath } from "@/components/app/nav-items";

// Minimal authenticated top bar (APP-1 §2). Left: mobile nav trigger + current section
// title with a mono system tag. Right: a small status indicator and the user menu.
// Deliberately sparse — no search, no clutter.
export function TopBar() {
  const { pathname } = useLocation();
  const title = titleForPath(pathname);

  return (
    <header className="flex h-16 shrink-0 items-center justify-between gap-4 border-b border-border bg-bg/80 px-4 backdrop-blur sm:px-6">
      <div className="flex items-center gap-4">
        <MobileNavigation />
        <div>
          <p className="label-system leading-none">Section</p>
          <h1 className="mt-1 text-base font-semibold leading-none text-foreground">{title}</h1>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <span className="hidden items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-muted-foreground sm:flex">
          <span
            aria-hidden
            className="inline-block size-1.5 rounded-full bg-emerald-400 [box-shadow:0_0_8px_rgb(52_211_153)]"
          />
          Secure
        </span>
        <UserMenu />
      </div>
    </header>
  );
}
