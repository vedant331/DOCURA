import { AnimatePresence, motion, useReducedMotion, type Variants } from "framer-motion";
import { useEffect, useRef, useState } from "react";

import { cn } from "@/lib/utils";

// HyperText — the scramble/decode wordmark effect (magicui / 21st.dev "hyper-text"), adapted
// for this Vite + Tailwind + TS codebase: the Next-only "use client" directive is dropped, and
// prefers-reduced-motion + accessibility are added. The letters are real text (an aria-label
// exposes the resolved word to assistive tech while the animated per-letter spans are hidden
// from it). font-mono keeps every glyph the same width, so scrambling causes no layout shift.

interface HyperTextProps {
  text: string;
  duration?: number;
  framerProps?: Variants;
  className?: string;
  animateOnLoad?: boolean;
}

const alphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

const getRandomInt = (max: number) => Math.floor(Math.random() * max);

export function HyperText({
  text,
  duration = 800,
  framerProps = {
    initial: { opacity: 0, y: -10 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 3 },
  },
  className,
  animateOnLoad = true,
}: HyperTextProps) {
  const [displayText, setDisplayText] = useState(text.split(""));
  const [trigger, setTrigger] = useState(false);
  const interations = useRef(0);
  const isFirstRender = useRef(true);
  const reducedMotion = useReducedMotion();

  const triggerAnimation = () => {
    if (reducedMotion) return; // no hover scramble when reduced motion is requested
    interations.current = 0;
    setTrigger(true);
  };

  useEffect(() => {
    // Reduced motion: never scramble. displayText already holds the real text, so it simply
    // renders statically and stays fully visible.
    if (reducedMotion) {
      setDisplayText(text.split(""));
      return;
    }
    const interval = setInterval(
      () => {
        if (!animateOnLoad && isFirstRender.current) {
          clearInterval(interval);
          isFirstRender.current = false;
          return;
        }
        if (interations.current < text.length) {
          setDisplayText((t) =>
            t.map((l, i) =>
              l === " "
                ? l
                : i <= interations.current
                  ? text[i]
                  : alphabets[getRandomInt(26)],
            ),
          );
          interations.current = interations.current + 0.1;
        } else {
          setTrigger(false);
          clearInterval(interval);
        }
      },
      duration / (text.length * 10),
    );
    // Clean up interval on unmount
    return () => clearInterval(interval);
  }, [text, duration, trigger, animateOnLoad, reducedMotion]);

  // Under reduced motion the per-letter entrance is neutralised too, so the word is present and
  // static rather than fading/moving in.
  const letterProps: Variants | undefined = reducedMotion ? undefined : framerProps;

  return (
    <div
      className="flex scale-100 cursor-default overflow-hidden py-2"
      onMouseEnter={triggerAnimation}
      aria-label={text}
      role="img"
    >
      <AnimatePresence mode="wait">
        {displayText.map((letter, i) => (
          <motion.span
            key={i}
            aria-hidden="true"
            className={cn("font-mono", letter === " " ? "w-3" : "", className)}
            {...letterProps}
          >
            {letter.toUpperCase()}
          </motion.span>
        ))}
      </AnimatePresence>
    </div>
  );
}
