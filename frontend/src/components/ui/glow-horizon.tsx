"use client";

import { motion } from "framer-motion";

// Adapted from the 21st.dev "glow-horizon" reference — SAME structure, motion and easing, but
// recoloured to DOCURA (Deep Navy + Lime). No purple/pink/magenta. A soft luminous horizon of
// arcs rises from an edge and settles, used behind the post-login greeting for a lime glow.

const EASE = [0.16, 1, 0.3, 1] as const;
const DURATION = 1.3;

export type GlowHorizonVariant = "top" | "bottom" | "left" | "right";

const VARIANTS: Record<
  GlowHorizonVariant,
  { axis: "x" | "y"; scaleAxis: "scaleX" | "scaleY"; enterPct: string; restPct: string }
> = {
  top: { axis: "y", scaleAxis: "scaleY", enterPct: "-100%", restPct: "-50%" },
  bottom: { axis: "y", scaleAxis: "scaleY", enterPct: "100%", restPct: "50%" },
  left: { axis: "x", scaleAxis: "scaleX", enterPct: "100%", restPct: "50%" },
  right: { axis: "x", scaleAxis: "scaleX", enterPct: "-100%", restPct: "-50%" },
};

export interface GlowHorizonProps {
  className?: string;
  variant?: GlowHorizonVariant;
}

export default function GlowHorizonFM({ className, variant = "top" }: GlowHorizonProps) {
  const { axis, scaleAxis, enterPct, restPct } = VARIANTS[variant];

  return (
    <motion.div
      className={"absolute h-full w-full " + (className ?? "")}
      style={{ isolation: "isolate" }}
      initial={{ [axis]: enterPct, [scaleAxis]: 1.5, opacity: 0, filter: "blur(15px)" }}
      animate={{ [axis]: restPct, [scaleAxis]: 1, opacity: 1, filter: "blur(0px)" }}
      transition={{ duration: DURATION, ease: EASE }}
    >
      {/* Lime + white + navy only — the reference's purple/indigo arcs are intentionally replaced. */}
      <Arc variant={variant} color="#FFFFFF" size="132%" boxShadow="0px -4px 23px 0px #ffffff55" delay={0.8} />
      <Arc variant={variant} color="#B8F35A" size="120%" initialOffset="10%" blur={31} delay={0.4} />
      <Arc variant={variant} color="#9DD63F" size="124%" initialOffset="10%" blur={21} delay={0} />
      <Arc variant={variant} color="#0E141C" size="120%" initialOffset="10%" blur={51} delay={0} />
    </motion.div>
  );
}

function Arc({
  variant,
  color,
  size,
  initialOffset,
  blur,
  boxShadow,
  delay,
}: {
  variant: GlowHorizonVariant;
  color: string;
  size: string;
  initialOffset?: string;
  blur?: number;
  boxShadow?: string;
  delay: number;
}) {
  const scale = parseFloat(size) / 100;
  const { axis, enterPct } = VARIANTS[variant];
  const sign = enterPct.startsWith("-") ? -1 : 1;
  const startPct = initialOffset
    ? `${sign * Math.abs(parseFloat(initialOffset) - 50)}%`
    : undefined;

  return (
    <motion.div
      aria-hidden
      className="absolute inset-0 rounded-[100%]"
      style={{
        scale,
        background: color,
        ...(blur !== undefined && { filter: `blur(${blur}px)` }),
        ...(boxShadow && { boxShadow }),
      }}
      initial={startPct ? { [axis]: startPct } : false}
      animate={startPct ? { [axis]: 0 } : undefined}
      transition={{ duration: DURATION, ease: EASE, delay }}
    />
  );
}
