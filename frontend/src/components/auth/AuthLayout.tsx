import { type ReactNode } from "react";

import { BlinkingSquares } from "@/components/ui/blinking-squares";

// Shared shell for every authentication screen (APP-1 §7). Near-black ground, the
// atmospheric background, a mono system id, a bold display heading, the form, and an
// optional footer of nav links. One layout keeps /login, /register, /forgot-password,
// and /reset-password unmistakably the same product.
export function AuthLayout({
  systemId,
  title,
  intro,
  children,
  footer,
  background,
}: {
  systemId: string;
  title: ReactNode;
  intro?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  // The decorative full-viewport background layer behind the card. Defaults to the shared
  // obsidian+lime BlinkingSquares used across every auth screen; a screen may still override.
  background?: ReactNode;
}) {
  return (
    <div className="relative flex min-h-screen w-full items-center justify-center bg-bg px-5 py-10">
      {background ?? <BlinkingSquares />}
      <main className="relative z-10 w-full max-w-[440px] animate-fade-in px-2 sm:px-0">
        {/* Obsidian card with a restrained lime hover glow and a traveling top light beam
            (adapted from the login reference's motion — no purple, no glass excess). */}
        <div className="group relative overflow-hidden rounded-md border border-border bg-surface/80 p-6 shadow-2xl shadow-black/40 backdrop-blur-sm transition-shadow duration-500 hover:shadow-accent-glow sm:p-8">
          <span aria-hidden className="auth-card-beam" />
          <header className="mb-8">
            <span className="label-system mb-2 block">{systemId}</span>
            <h1 className="text-[2.25rem] font-extrabold leading-[0.95] tracking-tight text-foreground sm:text-[2.75rem]">
              {title}
            </h1>
            {intro ? <p className="mt-4 max-w-sm text-sm text-muted-foreground">{intro}</p> : null}
          </header>
          {children}
          {footer ? (
            <footer className="mt-8 flex flex-wrap items-center justify-between gap-3 font-mono text-[10px] uppercase tracking-[0.2em]">
              {footer}
            </footer>
          ) : null}
        </div>
      </main>
    </div>
  );
}
