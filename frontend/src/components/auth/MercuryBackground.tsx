import { useEffect, useMemo, useRef } from "react";

import { cn } from "@/lib/utils";

// The atmospheric metallic-blob background from the Mercury reference, extracted as a
// reusable, performance-conscious primitive (APP-1 §5/§7). Decorative only: aria-hidden,
// pointer-events none, honours prefers-reduced-motion (via the global CSS rule), and
// uses a light parallax with rAF-free margin nudging that the browser can cheaply
// composite. `density` trims blob count on small screens so mobile stays smooth.
export function MercuryBackground({
  density = "full",
  className,
}: {
  density?: "full" | "sparse";
  className?: string;
}) {
  const count = density === "sparse" ? 4 : 6;

  const blobs = useMemo(
    () =>
      Array.from({ length: count }).map(() => ({
        size: Math.random() * 200 + 150,
        left: Math.random() * 80 + 10,
        top: Math.random() * 80 + 10,
        delay: Math.random() * -20,
        duration: Math.random() * 15 + 15,
      })),
    [count],
  );

  const refs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return; // no parallax when motion is reduced

    const onMove = (e: MouseEvent) => {
      const x = e.clientX / window.innerWidth;
      const y = e.clientY / window.innerHeight;
      refs.current.forEach((blob, i) => {
        if (!blob) return;
        const speed = (i + 1) * 16;
        blob.style.marginLeft = `${x * speed}px`;
        blob.style.marginTop = `${y * speed}px`;
      });
    };
    document.addEventListener("mousemove", onMove);
    return () => document.removeEventListener("mousemove", onMove);
  }, []);

  return (
    <div aria-hidden className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}>
      <svg className="absolute h-0 w-0">
        <defs>
          <filter id="docura-gooey">
            <feGaussianBlur in="SourceGraphic" stdDeviation="12" result="blur" />
            <feColorMatrix
              in="blur"
              mode="matrix"
              values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -9"
              result="goo"
            />
            <feComposite in="SourceGraphic" in2="goo" operator="atop" />
          </filter>
        </defs>
      </svg>

      <div className="absolute inset-0 opacity-50 [filter:url('#docura-gooey')]">
        {blobs.map((b, i) => (
          <div
            key={i}
            ref={(el) => {
              refs.current[i] = el;
            }}
            className="absolute animate-float rounded-full bg-gradient-to-br from-mercury to-mercury-dark blur-2xl transition-[margin] duration-100 ease-out [box-shadow:inset_-10px_-10px_20px_rgba(0,0,0,0.5),10px_10px_30px_rgba(255,255,255,0.15)]"
            style={{
              width: `${b.size}px`,
              height: `${b.size}px`,
              left: `${b.left}%`,
              top: `${b.top}%`,
              animationDelay: `${b.delay}s`,
              animationDuration: `${b.duration}s`,
            }}
          />
        ))}
      </div>
    </div>
  );
}
