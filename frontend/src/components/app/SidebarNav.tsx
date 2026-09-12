import { NavLink } from "react-router-dom";

import { NAV_ITEMS } from "@/components/app/nav-items";
import { cn } from "@/lib/utils";

// The navigation link list, shared by the desktop sidebar and the mobile drawer so both
// stay identical. Each row: mono code tag + icon + label, with a metallic active marker.
export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav aria-label="Primary" className="flex flex-col gap-1">
      {NAV_ITEMS.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                "group relative flex items-center gap-3 border-l-2 border-transparent px-3 py-2.5 text-sm transition-colors duration-200",
                "text-muted-foreground hover:bg-surface hover:text-foreground focus-visible:bg-surface",
                isActive && "border-mercury bg-surface text-foreground",
              )
            }
          >
            <span className="w-6 font-mono text-[10px] tracking-widest text-muted-foreground/70 group-hover:text-muted-foreground">
              {item.code}
            </span>
            <Icon className="size-4 shrink-0" aria-hidden />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        );
      })}
    </nav>
  );
}
