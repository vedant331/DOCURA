import { useEffect, useRef, type CSSProperties } from "react";

import { cn } from "@/lib/utils";

// "Dither Grid Gradient" (21st.dev). A coarse grid of square cells sampled across the palette ramp
// with Bayer ordered dithering, animated by sliding the ramp along the grid diagonal with a sine
// sweep (exactly 0 at ph=0, so motion never snaps), over a backdrop, with grain + vignette
// overlays. Canvas + requestAnimationFrame. Values are NOT quantised per frame (only the final
// per-cell colour is), so the motion does not visibly step. Decorative + pointer-events-none.
//
// Params come from the reference config (pixelCols/Rows, pixelAngle, pixelDither, pixelGap,
// speed 71 → ph = t*0.71, motionAmount 60 → amt 0.60). Under prefers-reduced-motion it renders a
// single static frame (ph=0). Pauses while the tab is hidden.

interface Stop {
  pos: number;
  r: number;
  g: number;
  b: number;
}

// Palette (sorted by position): Pine 0% → Moss 24% → Sprout 61% → Fern 67%.
const PALETTE: Stop[] = [
  { pos: 0.0, r: 14, g: 36, b: 23 }, // Pine  #0E2417
  { pos: 0.24, r: 46, g: 107, b: 62 }, // Moss  #2E6B3E
  { pos: 0.61, r: 221, g: 240, b: 200 }, // Sprout #DDF0C8
  { pos: 0.67, r: 120, g: 184, b: 107 }, // Fern  #78B86B
];
const BACKDROP = "#0E2417";
// 4×4 Bayer matrix (ordered dithering thresholds).
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
const GRAIN =
  "url(\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'>" +
  "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' " +
  "stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)' " +
  "opacity='0.5'/></svg>\")";

function sample(p: number): [number, number, number] {
  const c = p < 0 ? 0 : p > 1 ? 1 : p;
  if (c <= PALETTE[0].pos) return [PALETTE[0].r, PALETTE[0].g, PALETTE[0].b];
  const last = PALETTE[PALETTE.length - 1];
  if (c >= last.pos) return [last.r, last.g, last.b];
  for (let i = 0; i < PALETTE.length - 1; i++) {
    const a = PALETTE[i];
    const b = PALETTE[i + 1];
    if (c >= a.pos && c <= b.pos) {
      const t = (c - a.pos) / (b.pos - a.pos || 1);
      return [
        Math.round(a.r + (b.r - a.r) * t),
        Math.round(a.g + (b.g - a.g) * t),
        Math.round(a.b + (b.b - a.b) * t),
      ];
    }
  }
  return [last.r, last.g, last.b];
}

export function DitherGradient({ className, style }: { className?: string; style?: CSSProperties }) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef(0);

  useEffect(() => {
    const wrap = wrapRef.current;
    const canvas = canvasRef.current;
    if (!wrap || !canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const cols = 25;
    const rows = 15;
    const angle = (62 * Math.PI) / 180; // pixelAngle
    const norm = Math.cos(angle) + Math.sin(angle);
    const gap = 7 / 100; // pixelGap
    const ditherAmt = (76 / 100) * 0.18; // pixelDither → offset magnitude
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;

    let W = 1;
    let H = 1;
    let dpr = 1;
    const resize = () => {
      const rect = wrap.getBoundingClientRect();
      dpr = window.devicePixelRatio || 1;
      W = Math.max(1, Math.floor(rect.width));
      H = Math.max(1, Math.floor(rect.height));
      canvas.width = Math.floor(W * dpr);
      canvas.height = Math.floor(H * dpr);
      canvas.style.width = `${W}px`;
      canvas.style.height = `${H}px`;
    };

    const drawFrame = (elapsedSec: number) => {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = BACKDROP;
      ctx.fillRect(0, 0, W, H);

      const ph = elapsedSec * 0.71; // speed 71
      const amt = 0.6; // motionAmount 60
      const dir = 1; // motionReverse false
      const slide = Math.sin(ph * 0.9 * dir) * 0.5 * amt; // 0 at ph=0

      const cw = W / cols;
      const ch = H / rows;
      const gx = (cw * gap) / 2;
      const gy = (ch * gap) / 2;

      for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
          const nx = cols > 1 ? col / (cols - 1) : 0;
          const ny = rows > 1 ? row / (rows - 1) : 0;
          const uN = (nx * Math.cos(angle) + ny * Math.sin(angle)) / norm; // diagonal ramp position
          const th = (BAYER[(row % 4) * 4 + (col % 4)] + 0.5) / 16;
          const [r, g, b] = sample(uN + slide + (th - 0.5) * ditherAmt);
          ctx.fillStyle = `rgb(${r},${g},${b})`;
          ctx.fillRect(col * cw + gx, row * ch + gy, cw - gx * 2, ch - gy * 2);
        }
      }
    };

    resize();
    if (reduce) {
      drawFrame(0);
    } else {
      const start = performance.now();
      const loop = () => {
        if (!document.hidden) drawFrame((performance.now() - start) / 1000);
        rafRef.current = requestAnimationFrame(loop);
      };
      rafRef.current = requestAnimationFrame(loop);
    }

    let ro: ResizeObserver | null = null;
    const onResize = () => {
      resize();
      if (reduce) drawFrame(0);
    };
    if (typeof ResizeObserver !== "undefined") {
      ro = new ResizeObserver(onResize);
      ro.observe(wrap);
    } else {
      window.addEventListener("resize", onResize);
    }

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      if (ro) ro.disconnect();
      else window.removeEventListener("resize", onResize);
    };
  }, []);

  return (
    <div ref={wrapRef} className={cn("relative h-full w-full overflow-hidden", className)} style={style} aria-hidden>
      <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" />
      {/* Vignette (reference: radial darkening toward the edges). */}
      <div className="pointer-events-none absolute inset-0 [background:radial-gradient(circle_at_50%_50%,transparent_52%,rgba(0,0,0,0.8)_100%)]" />
      {/* Bitmap grain (reference SVG noise, overlay-blended, subtle). */}
      <div
        className="pointer-events-none absolute inset-0 opacity-40 [mix-blend-mode:overlay]"
        style={{ backgroundImage: GRAIN, backgroundSize: "120px 120px" }}
      />
    </div>
  );
}
