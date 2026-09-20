import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { motion } from "framer-motion";

import { cn } from "@/lib/utils";

// Sliding-cursor tab bar (adapted from the SlideTabs reference) — route-driven and themed to
// DOCURA Deep Navy + Lime. The lime pill slides under the hovered tab and rests under the active
// route on mouse-leave. Accessible: role="tablist"/"tab" with aria-selected and keyboard support.
export interface SlideTabItem {
  id: string; // the route to navigate to
  label: string;
}

interface CursorPosition {
  left: number;
  width: number;
  opacity: number;
}

export function SlideTabs({
  items,
  activeId,
  onSelect,
  className,
}: {
  items: SlideTabItem[];
  activeId: string;
  onSelect: (id: string) => void;
  className?: string;
}) {
  const selected = Math.max(
    0,
    items.findIndex((it) => it.id === activeId),
  );
  const [position, setPosition] = useState<CursorPosition>({ left: 0, width: 0, opacity: 0 });
  const tabsRef = useRef<(HTMLLIElement | null)[]>([]);

  const moveTo = (index: number) => {
    const el = tabsRef.current[index];
    if (!el) return;
    setPosition({ left: el.offsetLeft, width: el.getBoundingClientRect().width, opacity: 1 });
  };

  // Rest the cursor under the active route on mount and whenever it changes.
  useEffect(() => {
    moveTo(selected);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected, items.length]);

  const onKey = (e: KeyboardEvent<HTMLLIElement>, id: string) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onSelect(id);
    }
  };

  return (
    <ul
      role="tablist"
      className={cn(
        "relative flex w-fit items-center rounded-full border border-border bg-shell p-1",
        className,
      )}
    >
      {items.map((it, i) => (
        <li
          key={it.id}
          ref={(el) => {
            tabsRef.current[i] = el;
          }}
          role="tab"
          aria-selected={i === selected}
          tabIndex={0}
          onClick={() => onSelect(it.id)}
          onKeyDown={(e) => onKey(e, it.id)}
          className={cn(
            "relative z-10 block cursor-pointer select-none whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-medium uppercase tracking-wide transition-colors md:px-5 md:py-2.5 md:text-sm",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 focus-visible:ring-offset-shell",
            // Active: navy text on the filled lime pill. Inactive: muted grey, subtle navy hover.
            i === selected
              ? "text-accent-foreground"
              : "text-muted-foreground hover:bg-surface hover:text-foreground",
          )}
        >
          {it.label}
        </li>
      ))}

      {/* The sliding FILLED-lime active indicator. Tracks the active route (not hover) and
          slides/resizes smoothly between tabs on navigation. */}
      <motion.li
        aria-hidden
        animate={{ ...position }}
        transition={{ type: "spring", stiffness: 400, damping: 30 }}
        className="absolute top-1 z-0 h-7 rounded-full bg-accent md:h-10"
      />
    </ul>
  );
}
