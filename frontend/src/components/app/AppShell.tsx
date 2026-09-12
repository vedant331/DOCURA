import { Outlet } from "react-router-dom";

import { Sidebar } from "@/components/app/Sidebar";
import { TopBar } from "@/components/app/TopBar";

// The authenticated application shell (APP-1 §2). Desktop: fixed sidebar + top bar +
// scrollable content. Mobile: sidebar collapses to the drawer in the top bar. Child
// routes render into <Outlet/>. This is the foundation only — no product features (§11).
export function AppShell() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-bg text-foreground">
      <div className="hidden lg:block">
        <Sidebar />
      </div>
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar />
        <main className="flex-1 overflow-y-auto px-5 py-8 sm:px-8">
          <div className="mx-auto w-full max-w-5xl animate-fade-in">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
