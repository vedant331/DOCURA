import { motion, useReducedMotion, type Variants } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { useEffect, useState } from "react";

// -----------------------------------------------------------------------------------------
// HowItWorks — the 21st.dev "how-it-works" pinned floating-card timeline, adapted to DOCURA:
// the reference's white/orange/blue/purple + Comic Sans + its own gridded canvas are dropped,
// and everything is re-themed to Deep Navy surfaces + Lime with the project's Space Mono numbers.
// It reuses the already-installed framer-motion (the reference's `motion/react` import), renders
// no background of its own (the page's shader/section background shows through), and adds the
// scroll-reveal + reduced-motion handling the page uses elsewhere. Cards are decorative only.
//
// Desktop: cards float in a staggered left/right layout with a slight tilt, joined by a subtle
// dashed path. Mobile: cards stack vertically, straightened for readability, joined by a simple
// dashed rail. Content is supplied by the caller (Overview) — this file owns no copy.
// -----------------------------------------------------------------------------------------

export interface HowItWorksStep {
  title: string;
  description: string;
  icon?: LucideIcon;
}

interface HowItWorksProps {
  steps: HowItWorksStep[];
  className?: string;
}

// Decorative pin (from the reference), tinted to DOCURA lime.
function Pin({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden
      className={className}
    >
      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
      <path d="M16 3a1 1 0 0 1 .117 1.993l-.117 .007v4.764l1.894 3.789a1 1 0 0 1 .1 .331l.006 .116v2a1 1 0 0 1 -.883 .993l-.117 .007h-4v4a1 1 0 0 1 -1.993 .117l-.007 -.117v-4h-4a1 1 0 0 1 -.993 -.883l-.007 -.117v-2a1 1 0 0 1 .06 -.34l.046 -.107l1.894 -3.791v-4.762a1 1 0 0 1 -.117 -1.993l.117 -.007h8z" />
    </svg>
  );
}

// Desktop staggered positions + tilt (degrees). Same-side cards are kept ~470px apart so
// DOCURA's longer descriptions never overlap. Mobile straightens and stacks them.
const POSITIONS = [
  { className: "md:absolute md:top-0 md:left-[12%]", rotate: 3 },
  { className: "md:absolute md:top-[170px] md:right-[12%]", rotate: -3 },
  { className: "md:absolute md:top-[470px] md:left-[12%]", rotate: 3 },
  { className: "md:absolute md:top-[640px] md:right-[12%]", rotate: -3 },
  { className: "md:absolute md:top-[940px] md:left-[12%]", rotate: 2 },
];
const CANVAS_HEIGHT = 1240;
// Subtle dashed connector threading the (approx) card anchor points on desktop.
const CONNECTOR_PATH =
  "M 270 70 C 520 90, 520 220, 730 240 C 520 420, 520 400, 270 540 " +
  "C 520 660, 520 690, 730 710 C 520 900, 520 980, 270 1010";

function useIsMobile() {
  // Read synchronously on the first render so the tilt is correct from the initial paint:
  // framer memoises variants by label, so flipping the tilt after mount would not re-apply.
  const [isMobile, setIsMobile] = useState(
    () => typeof window !== "undefined" && window.matchMedia("(max-width: 767px)").matches,
  );
  useEffect(() => {
    const mq = window.matchMedia("(max-width: 767px)");
    const sync = () => setIsMobile(mq.matches);
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);
  return isMobile;
}

function cardVariants(rotate: number, reduced: boolean): Variants {
  if (reduced) {
    return { hidden: { opacity: 1, y: 0, rotate: 0 }, show: { opacity: 1, y: 0, rotate: 0 } };
  }
  return {
    hidden: { opacity: 0, y: 28, rotate },
    show: {
      opacity: 1,
      y: 0,
      rotate,
      transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] },
    },
  };
}

export function HowItWorks({ steps, className }: HowItWorksProps) {
  const reduced = useReducedMotion() ?? false;
  const isMobile = useIsMobile();

  const containerVariants: Variants = {
    hidden: {},
    show: { transition: { staggerChildren: reduced ? 0 : 0.12 } },
  };

  return (
    <div className={`relative mx-auto w-full max-w-[1000px] ${className ?? ""}`}>
      <motion.div
        className="relative flex h-auto flex-col space-y-6 md:block md:h-[var(--canvas)] md:space-y-0"
        style={{ ["--canvas" as string]: `${CANVAS_HEIGHT}px` }}
        variants={containerVariants}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, amount: 0.15 }}
      >
        {/* Mobile: a simple dashed rail behind the stacked cards (shows through the gaps). */}
        <div
          aria-hidden
          className="absolute inset-y-0 left-1/2 z-0 w-px -translate-x-1/2 border-l border-dashed border-accent/25 md:hidden"
        />

        {/* Desktop: the connecting dashed path threading the floating cards. */}
        {steps.length > 1 ? (
          <svg
            aria-hidden
            className="pointer-events-none absolute left-0 top-0 z-0 hidden h-full w-full md:block"
            viewBox={`0 0 1000 ${CANVAS_HEIGHT}`}
            preserveAspectRatio="none"
          >
            <motion.path
              d={CONNECTOR_PATH}
              className="text-accent/30"
              stroke="currentColor"
              strokeWidth="2"
              strokeDasharray="6 7"
              fill="none"
              strokeLinecap="round"
              vectorEffect="non-scaling-stroke"
              initial={{ strokeDashoffset: 0 }}
              animate={reduced ? undefined : { strokeDashoffset: -130 }}
              transition={reduced ? undefined : { duration: 3, repeat: Infinity, ease: "linear" }}
            />
          </svg>
        ) : null}

        {steps.map((step, index) => {
          const position = POSITIONS[index % POSITIONS.length];
          const tilt = reduced || isMobile ? 0 : position.rotate;
          const Icon = step.icon;
          return (
            <motion.div
              key={step.title}
              variants={cardVariants(tilt, reduced)}
              whileHover={reduced ? undefined : { scale: 1.03, zIndex: 30 }}
              className={`relative z-10 w-full md:w-[300px] ${position.className}`}
            >
              {/* Outer "pinned card" frame — subtle border + controlled shadow for depth. */}
              <div className="rounded-2xl border border-border bg-surface/80 p-2 shadow-lg shadow-black/25 backdrop-blur-sm">
                <Pin className="mx-auto mb-3 size-6 text-accent" />
                <div className="rounded-xl border border-border bg-surface-2/60 p-5">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-3xl font-bold tracking-tight text-accent">
                      {`0${index + 1}`}
                    </span>
                    {Icon ? <Icon className="size-5 text-muted-foreground" aria-hidden /> : null}
                  </div>
                  <h3 className="mt-4 text-lg font-semibold leading-tight text-foreground">
                    {step.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {step.description}
                  </p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </motion.div>
    </div>
  );
}
