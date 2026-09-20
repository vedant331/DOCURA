import { useEffect, useRef } from "react";

// Global click spark (React Bits ClickSpark, adapted). ONE instance mounts a fixed, full-viewport
// canvas that overlays the whole app and listens for clicks on the window, so every click
// anywhere sparks — no per-button wrapping. The canvas is pointer-events-none, so it never blocks
// clicks, inputs, scrolling, or navigation, and it adds no layout. Honours prefers-reduced-motion.
export interface ClickSparkProps {
  sparkColor?: string;
  sparkSize?: number; // spark line length (px)
  sparkRadius?: number; // how far sparks travel (px)
  sparkCount?: number; // sparks per click
  duration?: number; // ms
  easing?: "linear" | "ease-in" | "ease-out" | "ease-in-out";
  extraScale?: number; // multiplies travel distance
}

interface Spark {
  x: number;
  y: number;
  angle: number;
  start: number;
}

export function ClickSpark({
  sparkColor = "#B8F35A",
  sparkSize = 6,
  sparkRadius = 12,
  sparkCount = 6,
  duration = 300,
  easing = "ease-out",
  extraScale = 0.85,
}: ClickSparkProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return; // jsdom / no-canvas: no-op, never throws

    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
    if (reduce) return; // no sparks under reduced motion

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const resize = () => {
      canvas.width = Math.floor(window.innerWidth * dpr);
      canvas.height = Math.floor(window.innerHeight * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener("resize", resize);

    const ease = (t: number): number => {
      switch (easing) {
        case "linear":
          return t;
        case "ease-in":
          return t * t;
        case "ease-in-out":
          return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
        case "ease-out":
        default:
          return 1 - Math.pow(1 - t, 3);
      }
    };

    let sparks: Spark[] = [];
    let raf = 0;

    const draw = (now: number) => {
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
      sparks = sparks.filter((s) => now - s.start < duration);
      ctx.strokeStyle = sparkColor;
      ctx.lineWidth = 1.6;
      ctx.lineCap = "round";
      for (const s of sparks) {
        const t = (now - s.start) / duration;
        const eased = ease(t);
        const dist = eased * sparkRadius * extraScale;
        const len = sparkSize * (1 - eased);
        const cos = Math.cos(s.angle);
        const sin = Math.sin(s.angle);
        ctx.globalAlpha = 1 - eased;
        ctx.beginPath();
        ctx.moveTo(s.x + dist * cos, s.y + dist * sin);
        ctx.lineTo(s.x + (dist + len) * cos, s.y + (dist + len) * sin);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
      if (sparks.length > 0) {
        raf = requestAnimationFrame(draw);
      } else {
        raf = 0;
      }
    };

    const onClick = (e: MouseEvent) => {
      const now = performance.now();
      for (let i = 0; i < sparkCount; i++) {
        sparks.push({ x: e.clientX, y: e.clientY, angle: (2 * Math.PI * i) / sparkCount, start: now });
      }
      if (!raf) raf = requestAnimationFrame(draw);
    };
    window.addEventListener("click", onClick);

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("click", onClick);
      if (raf) cancelAnimationFrame(raf);
    };
  }, [sparkColor, sparkSize, sparkRadius, sparkCount, duration, easing, extraScale]);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden
      className="pointer-events-none fixed inset-0 z-[9999] h-full w-full"
    />
  );
}
