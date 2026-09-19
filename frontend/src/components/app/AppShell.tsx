import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { Command, LogOut, User } from "lucide-react";

import { useAuth } from "@/auth/AuthContext";
import { NAV_ITEMS } from "@/components/app/nav-items";
import {
  NotchNav,
  type NotchItemData,
} from "@/components/ui/adaptive-notch-navigation-bar";

// The authenticated application shell. The navigation chrome is the adaptive notch navigation
// (its visual design is the source of truth); it is wired to DOCURA's REAL routes, active-route
// detection, account, and sign-out. The routed content renders inside the notch content
// viewport: the chat workspace (/app) owns its full height; every other route scrolls within a
// centred max-width column, matching the previous behaviour.

// DOCURA's real destinations become the notch items (id = route). Labels/routes are unchanged.
const ITEMS: NotchItemData[] = NAV_ITEMS.map((item) => ({
  id: item.to,
  label: item.label,
  icon: item.icon,
}));

// Which nav item the current URL belongs to — same matching the sidebar used (longest route
// first; the index route matches exactly). Sub-routes (e.g. a document detail) keep their
// section highlighted; nested flows with no owning item fall back to Overview.
function activeIdForPath(pathname: string): string {
  const match = [...NAV_ITEMS]
    .sort((a, b) => b.to.length - a.to.length)
    .find((item) => (item.end ? pathname === item.to : pathname.startsWith(item.to)));
  return match?.to ?? "/app";
}

function LogoSlot() {
  return (
    <div className="flex h-7 items-center gap-1.5 sm:gap-2">
      <div className="flex size-5 items-center justify-center rounded-md bg-zinc-800 dark:bg-zinc-300">
        <Command className="size-3.5 text-zinc-50 dark:text-zinc-950" />
      </div>
      <span className="hidden text-xs font-bold tracking-tight sm:inline">DOCURA</span>
    </div>
  );
}

function AccountSlot({ initial, onSignOut }: { initial: string; onSignOut: () => void }) {
  return (
    <div className="flex h-7 items-center gap-1.5 sm:gap-2">
      <div className="hidden size-5 items-center justify-center rounded-full bg-zinc-800 text-[10px] font-bold text-zinc-300 sm:flex dark:bg-zinc-300 dark:text-zinc-800">
        {initial ? <span>{initial}</span> : <User className="size-3.5" />}
      </div>
      <button
        type="button"
        onClick={onSignOut}
        aria-label="Sign out"
        className="flex cursor-pointer items-center gap-1.5 text-xs font-medium text-zinc-400 outline-none hover:text-zinc-200 dark:text-zinc-600 dark:hover:text-zinc-900"
      >
        <span className="hidden sm:inline">Sign out</span>
        <LogOut className="size-4 sm:size-3.5" />
      </button>
    </div>
  );
}

export function AppShell() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, signOut } = useAuth();

  const activeId = activeIdForPath(pathname);
  const isChat = pathname === "/app" || pathname === "/app/";
  const initial = (user?.email ?? "").charAt(0).toUpperCase();

  const onSignOut = async () => {
    await signOut();
    navigate("/login", { replace: true });
  };

  return (
    <NotchNav
      items={ITEMS}
      activeId={activeId}
      logo={<LogoSlot />}
      rightContent={<AccountSlot initial={initial} onSignOut={onSignOut} />}
      onActiveChange={(id) => navigate(id)}
    >
      {isChat ? (
        // The chat workspace owns the full viewport height (internal scroll + sticky composer).
        <div className="h-full w-full">
          <Outlet />
        </div>
      ) : (
        // Every other route: scroll within a centred max-width column.
        <div className="h-full w-full overflow-y-auto">
          <div className="mx-auto w-full max-w-5xl py-2 animate-fade-in">
            <Outlet />
          </div>
        </div>
      )}
    </NotchNav>
  );
}
