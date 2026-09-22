import { motion, useReducedMotion, type Transition, type Variants } from "framer-motion";
import { useEffect, useState, type ElementType, type ReactNode } from "react";

// -----------------------------------------------------------------------------------------
// ScrollReveal — subtle, once-only entrance animations for page sections, built on the
// framer-motion the project already ships (no new dependency).
//
//   <Reveal>…</Reveal>                     one block fades + rises into view when scrolled to
//   <Reveal stagger>…<RevealItem/>…</Reveal>  its RevealItem children come in one after another
//   <Reveal onMount>…</Reveal>             plays on load instead of on scroll (used by the hero)
//
// Motion is opacity 0→1 + a small translateY (no X, so no horizontal overflow and no layout
// shift — transform/opacity only), plus a faint blur on desktop. It fires once (viewport.once)
// so a section never flickers on scroll-up. prefers-reduced-motion and small screens are
// honoured by rendering content plainly / with reduced distance. The shader background is a
// separate layer and is never touched here.
// -----------------------------------------------------------------------------------------

type Tag = "div" | "section" | "ol" | "li";

const EASE = [0.22, 1, 0.36, 1] as const; // smooth ease-out, no overshoot/bounce

function useMotionProfile(): { distance: number; blur: number; duration: number; stagger: number } {
  const [mobile, setMobile] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(max-width: 640px)");
    const sync = () => setMobile(mq.matches);
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);
  // Mobile: shorter travel, no blur, quicker — so the page never feels sluggish on a phone.
  return mobile
    ? { distance: 16, blur: 0, duration: 0.6, stagger: 0.06 }
    : { distance: 30, blur: 4, duration: 0.9, stagger: 0.1 };
}

function itemVariants(distance: number, blur: number, duration: number, delay: number): Variants {
  const transition: Transition = { duration, ease: EASE, delay };
  return {
    hidden: { opacity: 0, y: distance, filter: `blur(${blur}px)` },
    show: { opacity: 1, y: 0, filter: "blur(0px)", transition },
  };
}

function containerVariants(stagger: number, delay: number): Variants {
  return {
    hidden: {},
    show: { transition: { staggerChildren: stagger, delayChildren: delay } },
  };
}

const VIEWPORT = { once: true, amount: 0.2 } as const; // fire when ~20% of the block is visible

interface RevealProps {
  children: ReactNode;
  className?: string;
  as?: Tag;
  /** Orchestrate RevealItem children in sequence instead of animating as one block. */
  stagger?: boolean;
  /** Play on mount (page load) rather than when scrolled into view. For the hero. */
  onMount?: boolean;
  /** Extra delay before this block/its children begin (seconds). */
  delay?: number;
}

export function Reveal({
  children,
  className,
  as = "div",
  stagger = false,
  onMount = false,
  delay = 0,
}: RevealProps) {
  const reduced = useReducedMotion();
  const { distance, blur, duration, stagger: step } = useMotionProfile();
  const MotionTag = motion[as] as ElementType;

  // Reduced motion (or the rare no-JS matchMedia case): render the real element with no
  // animation so content is fully present and nothing depends on movement.
  if (reduced) {
    const Tag = as as ElementType;
    return <Tag className={className}>{children}</Tag>;
  }

  const variants = stagger
    ? containerVariants(step, delay)
    : itemVariants(distance, blur, duration, delay);

  const trigger = onMount
    ? { animate: "show" as const }
    : { whileInView: "show" as const, viewport: VIEWPORT };

  return (
    <MotionTag className={className} initial="hidden" variants={variants} {...trigger}>
      {children}
    </MotionTag>
  );
}

interface RevealItemProps {
  children: ReactNode;
  className?: string;
  as?: Tag;
}

/** A child of a `<Reveal stagger>` — inherits the parent's hidden/show timeline. */
export function RevealItem({ children, className, as = "div" }: RevealItemProps) {
  const reduced = useReducedMotion();
  const { distance, blur, duration } = useMotionProfile();
  const MotionTag = motion[as] as ElementType;

  if (reduced) {
    const Tag = as as ElementType;
    return <Tag className={className}>{children}</Tag>;
  }

  return (
    <MotionTag className={className} variants={itemVariants(distance, blur, duration, 0)}>
      {children}
    </MotionTag>
  );
}
