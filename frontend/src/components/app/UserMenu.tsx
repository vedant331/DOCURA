import { useNavigate } from "react-router-dom";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ChevronDown, LogOut, Settings as SettingsIcon, UserSquare } from "lucide-react";

import { useAuth } from "@/auth/AuthContext";
import { cn } from "@/lib/utils";

// Reusable profile menu (APP-1 §3). Shows the authenticated email, a settings shortcut,
// and logout. Logout calls the real backend revocation via useAuth().signOut — never a
// fake local-only state change.
export function UserMenu({ align = "end" }: { align?: "start" | "end" }) {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const email = user?.email ?? "unknown";
  const initial = email.charAt(0).toUpperCase();

  const onSignOut = async () => {
    await signOut();
    navigate("/login", { replace: true });
  };

  const itemClass =
    "flex cursor-pointer items-center gap-2.5 px-3 py-2 text-sm text-muted-foreground outline-none transition-colors data-[highlighted]:bg-surface data-[highlighted]:text-foreground";

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger
        className={cn(
          "flex items-center gap-2.5 border border-border bg-surface/60 px-2.5 py-1.5 text-left transition-colors",
          "hover:border-mercury/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        )}
        aria-label="Account menu"
      >
        <span className="flex size-7 items-center justify-center bg-primary font-mono text-xs font-bold text-primary-foreground">
          {initial}
        </span>
        <span className="hidden max-w-[160px] truncate font-mono text-xs text-muted-foreground sm:inline">
          {email}
        </span>
        <ChevronDown className="size-3.5 text-muted-foreground" aria-hidden />
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align={align}
          sideOffset={8}
          className="z-50 min-w-[220px] animate-fade-in border border-border bg-surface-2 p-1 shadow-2xl"
        >
          <div className="px-3 py-2">
            <p className="label-system mb-1">Signed in as</p>
            <p className="truncate text-sm text-foreground">{email}</p>
          </div>
          <DropdownMenu.Separator className="my-1 h-px bg-border" />
          <DropdownMenu.Item className={itemClass} onSelect={() => navigate("/app/record")}>
            <UserSquare className="size-4" aria-hidden />
            My Record
          </DropdownMenu.Item>
          <DropdownMenu.Item className={itemClass} onSelect={() => navigate("/app/settings")}>
            <SettingsIcon className="size-4" aria-hidden />
            Settings
          </DropdownMenu.Item>
          <DropdownMenu.Separator className="my-1 h-px bg-border" />
          <DropdownMenu.Item
            className={cn(itemClass, "text-destructive data-[highlighted]:text-destructive")}
            onSelect={(e) => {
              e.preventDefault();
              void onSignOut();
            }}
          >
            <LogOut className="size-4" aria-hidden />
            Sign Out
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
