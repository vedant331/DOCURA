import { Activity, FileText, LayoutGrid, MessageSquare, UserSquare, type LucideIcon } from "lucide-react";

// The authenticated navigation, defined once so the sidebar and the mobile drawer never
// drift apart (APP-1 §2/§7). Overview is the informational landing surface; Ask is the AI
// chat workspace (the surface that previously lived at the index route). Settings stays a
// real route but is reached from the account avatar rather than the primary nav.
export interface NavItem {
  to: string;
  label: string;
  code: string; // mono system tag, DOCURA style
  icon: LucideIcon;
  end?: boolean; // exact match (for routes with no sub-routes)
}

export const NAV_ITEMS: NavItem[] = [
  { to: "/overview", label: "Overview", code: "00", icon: LayoutGrid, end: true },
  { to: "/ask", label: "Ask", code: "01", icon: MessageSquare, end: true },
  { to: "/documents", label: "Documents", code: "02", icon: FileText },
  { to: "/record", label: "My Record", code: "03", icon: UserSquare },
  { to: "/activity", label: "Activity", code: "04", icon: Activity },
];

export function titleForPath(pathname: string): string {
  const match = [...NAV_ITEMS]
    .sort((a, b) => b.to.length - a.to.length)
    .find((i) => (i.end ? pathname === i.to : pathname.startsWith(i.to)));
  return match?.label ?? "Overview";
}
