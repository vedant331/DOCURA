import { Activity, FileText, LayoutGrid, Settings, UserSquare, type LucideIcon } from "lucide-react";

// The authenticated navigation, defined once so the sidebar and the mobile drawer never
// drift apart (APP-1 §2/§7). These are foundation destinations only — APP-1 builds the
// shell, not the features behind them (§11).
export interface NavItem {
  to: string;
  label: string;
  code: string; // mono system tag, DOCURA style
  icon: LucideIcon;
  end?: boolean; // exact match (for the index route)
}

export const NAV_ITEMS: NavItem[] = [
  { to: "/app", label: "Overview", code: "00", icon: LayoutGrid, end: true },
  { to: "/app/documents", label: "Documents", code: "01", icon: FileText },
  { to: "/app/record", label: "My Record", code: "02", icon: UserSquare },
  { to: "/app/activity", label: "Activity", code: "03", icon: Activity },
  { to: "/app/settings", label: "Settings", code: "04", icon: Settings },
];

export function titleForPath(pathname: string): string {
  const match = [...NAV_ITEMS]
    .sort((a, b) => b.to.length - a.to.length)
    .find((i) => (i.end ? pathname === i.to : pathname.startsWith(i.to)));
  return match?.label ?? "Overview";
}
