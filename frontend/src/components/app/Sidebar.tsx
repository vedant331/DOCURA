import { useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";

import { useAuth } from "@/auth/AuthContext";
import { Brand } from "@/components/app/Brand";
import { SidebarNav } from "@/components/app/SidebarNav";
import { cn } from "@/lib/utils";

// Desktop left navigation (APP-1 §2). Dark monochrome surface, thin right border, mono
// system tags, and a profile/logout area pinned to the bottom. Not a generic admin
// template — it continues the auth screens' visual language.
export function Sidebar() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const onSignOut = async () => {
    await signOut();
    navigate("/login", { replace: true });
  };

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-border bg-surface/40">
      <div className="border-b border-border px-5 py-5">
        <Brand />
        <p className="label-system mt-3">Personal Document Intelligence</p>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-4">
        <SidebarNav />
      </div>

      <div className="border-t border-border p-3">
        <div className="mb-2 flex items-center gap-3 px-2 py-2">
          <span className="flex size-8 shrink-0 items-center justify-center bg-primary font-mono text-xs font-bold text-primary-foreground">
            {(user?.email ?? "?").charAt(0).toUpperCase()}
          </span>
          <div className="min-w-0">
            <p className="label-system">Operator</p>
            <p className="truncate text-xs text-foreground">{user?.email ?? "unknown"}</p>
          </div>
        </div>
        <button
          type="button"
          onClick={onSignOut}
          className={cn(
            "flex w-full items-center gap-2.5 px-2 py-2 text-sm text-muted-foreground transition-colors",
            "hover:bg-surface hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
          )}
        >
          <LogOut className="size-4" aria-hidden />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
