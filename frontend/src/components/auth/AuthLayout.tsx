import { type ReactNode } from "react";

import { MercuryBackground } from "@/components/auth/MercuryBackground";

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
}: {
  systemId: string;
  title: ReactNode;
  intro?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <div className="relative flex min-h-screen w-full items-center justify-center bg-bg px-5 py-10">
      <MercuryBackground />
      <main className="relative z-10 w-full max-w-[440px] animate-fade-in px-2 sm:px-6">
        <header className="mb-12">
          <span className="label-system mb-2 block">{systemId}</span>
          <h1 className="text-[2.5rem] font-extrabold leading-[0.9] tracking-tight text-foreground sm:text-5xl">
            {title}
          </h1>
          {intro ? <p className="mt-4 max-w-sm text-sm text-muted-foreground">{intro}</p> : null}
        </header>
        {children}
        {footer ? (
          <footer className="mt-10 flex flex-wrap items-center justify-between gap-3 font-mono text-[10px] uppercase tracking-[0.2em]">
            {footer}
          </footer>
        ) : null}
      </main>
    </div>
  );
}
