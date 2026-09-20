import { useEffect, useState, type RefObject } from "react";

// The ONLY visible scroll cue in DOCURA: a thin lime line fixed to the very top of the viewport
// that grows left→right with the CURRENT page's scroll position (0% at top, 100% at bottom).
//
// Route/page aware: it measures the live scroll container (`targetRef`) — the actual scroll
// position and scroll height of the currently-rendered route — never a global accumulator. The
// effect re-runs on `routeKey` (the pathname) so navigation recomputes for the new page and
// re-attaches to its container; a page that opens at the top reads 0%, a page with no scrollable
// overflow reads 0%. Scroll/resize are rAF-throttled and content-size changes are picked up via
// ResizeObserver. State only updates when the rounded percentage actually changes, so it does not
// re-render on every scroll frame. Decorative + pointer-events-none: it never blocks scrolling.
export function ScrollProgress({
  targetRef,
  routeKey,
}: {
  targetRef: RefObject<HTMLElement | null>;
  routeKey?: string;
}) {
  const [pct, setPct] = useState(0);

  useEffect(() => {
    let raf = 0;

    const compute = () => {
      raf = 0;
      const node = targetRef.current;
      if (!node) {
        setPct((prev) => (prev === 0 ? prev : 0));
        return;
      }
      const { scrollTop, scrollHeight, clientHeight } = node;
      const max = scrollHeight - clientHeight;
      const next = max > 1 ? Math.min(100, Math.max(0, (scrollTop / max) * 100)) : 0;
      // Round to avoid sub-pixel churn; only setState when the value meaningfully changes.
      const rounded = Math.round(next * 10) / 10;
      setPct((prev) => (prev === rounded ? prev : rounded));
    };

    const schedule = () => {
      if (!raf) raf = requestAnimationFrame(compute);
    };

    compute(); // initial (and recompute for the new route on navigation)

    const node = targetRef.current;
    if (!node) return; // e.g. a full-height route with no outer scroll container → stays 0%

    node.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule);
    // Recalculate when the page's content size changes dynamically (lazy content, expanding lists).
    const ro = typeof ResizeObserver !== "undefined" ? new ResizeObserver(schedule) : null;
    ro?.observe(node);
    if (node.firstElementChild) ro?.observe(node.firstElementChild);

    return () => {
      node.removeEventListener("scroll", schedule);
      window.removeEventListener("resize", schedule);
      ro?.disconnect();
      if (raf) cancelAnimationFrame(raf);
    };
  }, [targetRef, routeKey]);

  return (
    <div aria-hidden className="pointer-events-none fixed inset-x-0 top-0 z-[60] h-[3px]">
      <div className="h-full bg-primary" style={{ width: `${pct}%` }} />
    </div>
  );
}
