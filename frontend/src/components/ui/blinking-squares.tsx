import { useEffect, useRef } from "react";

import { cn } from "@/lib/utils";

// DOCURA login background: a deep-obsidian canvas with a sparse grid of small lime squares that
// quietly twinkle. Dependency-free (canvas 2D) — the same effect as React Bits Pro's
// "blinking squares", tuned to DOCURA's obsidian+lime tokens. Decorative only: full-viewport,
// aria-hidden, pointer-events-none, and static under prefers-reduced-motion. It draws lime on a
// transparent canvas; the obsidian ground comes from the page behind it.
export interface BlinkingSquaresProps {
  gridSize?: number; // cell pitch in px
  squareSize?: number; // fraction of a cell the square fills (0..1)
  fadeStart?: number; // radial fade start (0=center .. 1=corner) — squares stay dim near center
  fadeEnd?: number; // radial fade end
  minBrightness?: number; // brightness floor of a twinkle
  twinkleSpeed?: number; // radians/second
  twinkleStrength?: number; // twinkle amplitude
  intensity?: number; // overall max alpha multiplier
  opacity?: number; // canvas-wide alpha
  color?: string; // base lime
  highlight?: string; // brighter lime for peaks
  className?: string;
}

function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace("#", "");
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

export function BlinkingSquares({
  gridSize = 52,
  squareSize = 0.48,
  fadeStart = 0.32,
  fadeEnd = 1,
  minBrightness = 0.28,
  twinkleSpeed = 0.9,
  twinkleStrength = 0.55,
  intensity = 0.55,
  opacity = 0.45,
  color = "#B8F35A",
  highlight = "#C9FF78",
  className,
}: BlinkingSquaresProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return; // jsdom / no-canvas: render nothing, never throw

    const [br, bg, bb] = hexToRgb(color);
    const [hr, hg, hb] = hexToRgb(highlight);
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;

    let width = 0;
    let height = 0;
    // Stable per-cell phase + a sparse on/off mask, seeded once from the grid position.
    let phases: Float32Array = new Float32Array(0);
    let cols = 0;
    let rows = 0;

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const rect = canvas.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      canvas.width = Math.max(1, Math.floor(width * dpr));
      canvas.height = Math.max(1, Math.floor(height * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      cols = Math.ceil(width / gridSize) + 1;
      rows = Math.ceil(height / gridSize) + 1;
      phases = new Float32Array(cols * rows);
      for (let i = 0; i < phases.length; i++) {
        // Deterministic pseudo-random phase; ~45% of cells are effectively dormant (sparse).
        const r = Math.sin(i * 12.9898) * 43758.5453;
        phases[i] = (r - Math.floor(r)) * Math.PI * 2;
      }
    };

    const side = gridSize * squareSize;
    const maxR = () => Math.hypot(width, height) / 2 || 1;

    const draw = (tSec: number) => {
      ctx.clearRect(0, 0, width, height);
      const cx = width / 2;
      const cy = height / 2;
      const rMax = maxR();
      for (let gx = 0; gx < cols; gx++) {
        for (let gy = 0; gy < rows; gy++) {
          const i = gx * rows + gy;
          const phase = phases[i];
          // Sparse: cells whose phase lands in a band stay dark, keeping the field quiet.
          if (phase < 1.1) continue;
          const px = gx * gridSize;
          const py = gy * gridSize;
          const dist = Math.hypot(px - cx, py - cy) / rMax; // 0 center .. ~1 corner
          const fade = Math.min(1, Math.max(0, (dist - fadeStart) / (fadeEnd - fadeStart)));
          if (fade <= 0.001) continue;
          const wave = reduce ? 0.5 : 0.5 * (1 + Math.sin(tSec * twinkleSpeed + phase));
          const brightness = Math.min(1, minBrightness + twinkleStrength * wave);
          const alpha = opacity * intensity * fade * brightness;
          if (alpha < 0.01) continue;
          // Peak twinkles lean toward the brighter lime.
          const mix = Math.max(0, brightness - 0.7) / 0.3;
          const cr = Math.round(br + (hr - br) * mix);
          const cg = Math.round(bg + (hg - bg) * mix);
          const cb = Math.round(bb + (hb - bb) * mix);
          ctx.fillStyle = `rgba(${cr},${cg},${cb},${alpha.toFixed(3)})`;
          ctx.fillRect(px - side / 2, py - side / 2, side, side);
        }
      }
    };

    let raf = 0;
    const loop = (now: number) => {
      draw(now / 1000);
      raf = requestAnimationFrame(loop);
    };

    resize();
    if (reduce) {
      draw(0); // one static frame; no animation loop
    } else {
      raf = requestAnimationFrame(loop);
    }
    window.addEventListener("resize", resize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, [
    gridSize,
    squareSize,
    fadeStart,
    fadeEnd,
    minBrightness,
    twinkleSpeed,
    twinkleStrength,
    intensity,
    opacity,
    color,
    highlight,
  ]);

  return (
    <div aria-hidden className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}>
      <canvas ref={canvasRef} className="h-full w-full" />
    </div>
  );
}
