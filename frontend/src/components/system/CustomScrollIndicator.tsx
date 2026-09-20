import { useEffect, useRef, useState, type RefObject } from "react";

import { cn } from "@/lib/utils";

// A minimal, DOCURA-styled scroll indicator overlaid on a scroll container's right edge. The
// native scrollbar is hidden globally (see index.css); this renders the visible cue instead:
// a thin rounded thumb that tracks scroll position, fades in while scrolling and out after a
// short idle, and brightens navy -> lime while scrolling. Decorative + pointer-events-none, so
// it never blocks wheel/trackpad/keyboard scrolling, selection, or interaction. It adds no
// layout width. Under prefers-reduced-motion it stays quietly visible with no fade/colour shift.
export function CustomScrollIndicator({
  targetRef,
  className,
}: {
  targetRef: RefObject<HTMLElement | null>;
  className?: string;
}) {
  const [thumb, setThumb] = useState({ height: 0, top: 0 });
  const [visible, setVisible] = useState(false);
  const [scrolling, setScrolling] = useState(false);
  const idle = useRef<number | null>(null);

  useEffect(() => {
    const el = targetRef.current;
    if (!el) return;
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;

    const update = () => {
      const { scrollTop, scrollHeight, clientHeight } = el;
      if (scrollHeight <= clientHeight + 1) {
        setThumb({ height: 0, top: 0 });
        return;
      }
      const h = Math.max(28, (clientHeight / scrollHeight) * clientHeight);
      const top = (scrollTop / (scrollHeight - clientHeight)) * (clientHeight - h);
      setThumb({ height: h, top });
    };

    const onScroll = () => {
      update();
      setVisible(true);
      if (reduce) return; // functional position tracking only; no fade/colour animation
      setScrolling(true);
      if (idle.current) window.clearTimeout(idle.current);
      idle.current = window.setTimeout(() => {
        setScrolling(false);
        setVisible(false);
      }, 900);
    };

    update();
    if (reduce) setVisible(true);
    el.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", update);
    // ResizeObserver isn't present in every environment (e.g. jsdom); use it when available.
    const ro = typeof ResizeObserver !== "undefined" ? new ResizeObserver(update) : null;
    ro?.observe(el);
    return () => {
      el.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", update);
      ro?.disconnect();
      if (idle.current) window.clearTimeout(idle.current);
    };
  }, [targetRef]);

  if (thumb.height === 0) return null;

  return (
    <div
      aria-hidden
      className={cn("pointer-events-none absolute inset-y-0 right-1 z-30 w-1.5", className)}
    >
      <div
        className={cn(
          "absolute right-0 w-full rounded-full transition-[background-color,opacity] duration-300 ease-out",
          scrolling ? "bg-accent" : "bg-border",
          visible ? "opacity-100" : "opacity-0",
        )}
        style={{ height: `${thumb.height}px`, transform: `translateY(${thumb.top}px)` }}
      />
    </div>
  );
}
