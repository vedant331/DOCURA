import { useState } from "react";
import { useNavigate } from "react-router-dom";
import * as Dialog from "@radix-ui/react-dialog";
import { LogOut, Menu, X } from "lucide-react";

import { useAuth } from "@/auth/AuthContext";
import { Brand } from "@/components/app/Brand";
import { SidebarNav } from "@/components/app/SidebarNav";

// Mobile navigation as a slide-in drawer (APP-1 §5). The same nav list as the desktop
// sidebar, so the two never diverge. The trigger lives in the top bar on small screens.
export function MobileNavigation() {
  const [open, setOpen] = useState(false);
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const onSignOut = async () => {
    setOpen(false);
    await signOut();
    navigate("/login", { replace: true });
  };

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger
        className="flex size-9 items-center justify-center border border-border text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring lg:hidden"
        aria-label="Open navigation"
      >
        <Menu className="size-5" aria-hidden />
      </Dialog.Trigger>

      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm data-[state=open]:animate-fade-in lg:hidden" />
        <Dialog.Content
          className="fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col border-r border-border bg-surface-2 focus:outline-none lg:hidden"
          aria-label="Navigation"
        >
          <div className="flex items-center justify-between border-b border-border px-5 py-5">
            <Brand />
            <Dialog.Close
              className="flex size-8 items-center justify-center text-muted-foreground hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              aria-label="Close navigation"
            >
              <X className="size-5" aria-hidden />
            </Dialog.Close>
          </div>

          <Dialog.Title className="sr-only">DOCURA navigation</Dialog.Title>
          <div className="flex-1 overflow-y-auto px-3 py-4">
            <SidebarNav onNavigate={() => setOpen(false)} />
          </div>

          <div className="border-t border-border p-3">
            <p className="label-system mb-2 px-2">{user?.email ?? "unknown"}</p>
            <button
              type="button"
              onClick={onSignOut}
              className="flex w-full items-center gap-2.5 px-2 py-2 text-sm text-muted-foreground hover:bg-surface hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <LogOut className="size-4" aria-hidden />
              Sign Out
            </button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
