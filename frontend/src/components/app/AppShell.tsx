import { useRef } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { Command, LogOut } from "lucide-react";

import { useAuth } from "@/auth/AuthContext";
import { NAV_ITEMS } from "@/components/app/nav-items";
import { SlideTabs, type SlideTabItem } from "@/components/ui/slide-tabs";
import { CustomScrollIndicator } from "@/components/system/CustomScrollIndicator";

// The authenticated application shell. The navigation is the SlideTabs bar wired to DOCURA's REAL
// routes + active-route detection; the top bar also carries the brand mark and sign-out. The
// routed content renders inside the viewport below: the chat workspace (/app) owns its full
// height, every other route scrolls within a centred max-width column (unchanged behaviour).

// DOCURA's real destinations become the tabs (id = route). Labels/routes are unchanged.
const ITEMS: SlideTabItem[] = NAV_ITEMS.map((item) => ({ id: item.to, label: item.label }));

// Which nav item the current URL belongs to (longest route first; the index route matches
// exactly). Sub-routes keep their section active; nested flows fall back to Overview.
function activeIdForPath(pathname: string): string {
  const match = [...NAV_ITEMS]
    .sort((a, b) => b.to.length - a.to.length)
    .find((item) => (item.end ? pathname === item.to : pathname.startsWith(item.to)));
  return match?.to ?? "/app";
}

export function AppShell() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, signOut } = useAuth();

  const activeId = activeIdForPath(pathname);
  const isChat = pathname === "/app" || pathname === "/app/";
  const initial = (user?.email ?? "").charAt(0).toUpperCase();
  const scrollRef = useRef<HTMLDivElement>(null);

  const onSignOut = async () => {
    await signOut();
    navigate("/login", { replace: true });
  };

  return (
    <div className="flex h-screen w-full flex-col bg-bg text-foreground">
      <header className="flex items-center justify-between gap-3 border-b border-border bg-shell px-4 py-2.5 sm:px-6">
        {/* Brand mark */}
        <div className="flex shrink-0 items-center gap-2">
          <div className="flex size-6 items-center justify-center rounded-md bg-accent">
            <Command className="size-3.5 text-accent-foreground" aria-hidden />
          </div>
          <span className="hidden text-sm font-bold tracking-tight text-foreground sm:inline">
            DOCURA
          </span>
        </div>

        {/* Primary navigation — the SlideTabs bar (scrolls horizontally if it must). */}
        <nav aria-label="Primary" className="min-w-0 flex-1 overflow-x-auto">
          <SlideTabs
            items={ITEMS}
            activeId={activeId}
            onSelect={(id) => navigate(id)}
            className="mx-auto"
          />
        </nav>

        {/* Account + sign-out */}
        <div className="flex shrink-0 items-center gap-2">
          <div className="hidden size-6 items-center justify-center rounded-full bg-surface-2 text-[10px] font-bold text-muted-foreground sm:flex">
            {initial || <span aria-hidden>·</span>}
          </div>
          {/* Compact animated pill (ButtonWithIcon pattern): on hover the icon slides across and
              rotates, spacing swaps, and border/text/icon shift to DOCURA lime. Real <button>,
              same onSignOut handler — logout behaviour is unchanged. */}
          <button
            type="button"
            onClick={onSignOut}
            aria-label="Sign out"
            className="group relative flex h-8 shrink-0 cursor-pointer items-center overflow-hidden rounded-full border border-border bg-shell pl-3 pr-9 text-xs font-medium text-muted-foreground outline-none transition-all duration-300 hover:border-accent hover:pl-9 hover:pr-3 hover:text-accent active:border-primary-hover active:text-primary-hover focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 focus-visible:ring-offset-shell"
          >
            <span className="relative z-10 whitespace-nowrap transition-all duration-300">
              Sign out
            </span>
            <span
              aria-hidden
              className="absolute right-1 flex size-6 items-center justify-center rounded-full bg-surface-2 text-muted-foreground transition-all duration-300 group-hover:right-[calc(100%-28px)] group-hover:rotate-45 group-hover:bg-accent-soft group-hover:text-accent group-active:text-primary-hover"
            >
              <LogOut className="size-3.5" />
            </span>
          </button>
        </div>
      </header>

      <div className="min-h-0 flex-1">
        {isChat ? (
          // The chat workspace owns the full viewport height (internal scroll + sticky composer).
          <div className="h-full w-full">
            <Outlet />
          </div>
        ) : (
          // Every other route: scroll within a centred max-width column, with the custom
          // DOCURA scroll indicator overlaid on the container's right edge.
          <div className="relative h-full w-full">
            <div ref={scrollRef} className="h-full w-full overflow-y-auto">
              <div className="mx-auto w-full max-w-5xl px-4 py-4 animate-fade-in">
                <Outlet />
              </div>
            </div>
            <CustomScrollIndicator targetRef={scrollRef} />
          </div>
        )}
      </div>
    </div>
  );
}
