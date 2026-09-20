import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";

import GlowHorizonFM from "@/components/ui/glow-horizon";

// The post-authentication brand moment: DOCURA acknowledges the user AFTER a successful sign-in
// and BEFORE the workspace. It renders full-screen OVER the still-mounted login grid (visual
// continuity), layers the lime GlowHorizon (adapted from the reference — no purple), reveals
// "Docura Says Hello" with a staged, overlapping motion (easing [0.16, 1, 0.3, 1]), holds briefly,
// then raises a Deep-Navy veil so the route change into the existing destination (also navy) is
// seamless — no flash, no blank screen. It calls onDone at the end, which performs the
// (unchanged) navigation. GPU-friendly transform/opacity. Total ≈ 2.1s (within 1.5–2.5s).
//
// Under prefers-reduced-motion the same stages run quickly without transforms, so the user always
// reaches the app and never sees a hard cut.

const EASE = [0.16, 1, 0.3, 1] as const;

const WORD_DURATION = 0.7;
const WORD_STAGGER = 0.09;
const REVEAL_MS = 900; // word entrance settles
const HOLD_MS = 700; // readable hold
const EXIT_MS = 500; // navy veil in

const WORDS: { text: string; lime?: boolean }[] = [
  { text: "Docura" },
  { text: "Says" },
  { text: "Hello", lime: true },
];

export function LoginGreeting({ onDone }: { onDone: () => void }) {
  const reduce = useReducedMotion();
  const [exiting, setExiting] = useState(false);

  const revealMs = reduce ? 150 : REVEAL_MS;
  const holdMs = reduce ? 350 : HOLD_MS;
  const exitMs = reduce ? 200 : EXIT_MS;

  useEffect(() => {
    const toExit = window.setTimeout(() => setExiting(true), revealMs + holdMs);
    return () => window.clearTimeout(toExit);
  }, [revealMs, holdMs]);

  useEffect(() => {
    if (!exiting) return;
    const toDone = window.setTimeout(onDone, exitMs);
    return () => window.clearTimeout(toDone);
  }, [exiting, exitMs, onDone]);

  return (
    <div className="fixed inset-0 z-[60] overflow-hidden" role="status" aria-live="polite">
      {/* Greeting layer — transparent, so the login grid continues directly behind it. */}
      <motion.div
        className="absolute inset-0 flex items-center justify-center px-6"
        initial={{ opacity: 1 }}
        animate={{ opacity: exiting ? 0 : 1 }}
        transition={{ duration: exitMs / 1000, ease: EASE }}
      >
        {/* Lime glow horizon (reference motion, DOCURA colours). Screen-blended + softened so it
            adds light over the grid rather than covering it. */}
        {!reduce ? (
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 opacity-70 [mix-blend-mode:screen]"
          >
            <GlowHorizonFM variant="top" />
          </div>
        ) : null}

        <motion.h1
          className="relative text-center text-4xl font-extrabold tracking-tight text-foreground sm:text-6xl"
          initial="hidden"
          animate="show"
          variants={{
            hidden: {},
            show: {
              transition: {
                staggerChildren: reduce ? 0 : WORD_STAGGER,
                delayChildren: reduce ? 0 : 0.12,
              },
            },
          }}
        >
          {WORDS.map((word, i) => (
            <motion.span
              key={i}
              className={`inline-block ${word.lime ? "text-primary" : ""} ${i > 0 ? "ml-[0.3em]" : ""}`}
              variants={{
                hidden: reduce ? { opacity: 0 } : { opacity: 0, y: "0.5em", filter: "blur(6px)" },
                show: { opacity: 1, y: "0em", filter: "blur(0px)" },
              }}
              transition={{ duration: reduce ? 0.15 : WORD_DURATION, ease: EASE }}
              style={word.lime ? { textShadow: "0 0 28px hsl(var(--accent) / 0.5)" } : undefined}
            >
              {word.text}
            </motion.span>
          ))}
        </motion.h1>
      </motion.div>

      {/* Deep-Navy exit veil — fades in over grid + greeting so the handoff into the existing
          (navy) destination is seamless; the app mounts navy behind it, so there is no flash. */}
      <motion.div
        aria-hidden
        className="absolute inset-0 bg-bg"
        initial={{ opacity: 0 }}
        animate={{ opacity: exiting ? 1 : 0 }}
        transition={{ duration: exitMs / 1000, ease: EASE }}
      />
    </div>
  );
}
