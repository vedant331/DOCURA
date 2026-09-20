import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

// A tiny transient signal for the post-login brand greeting. It exists so PublicRoute can DEFER
// its "authenticated → /app" redirect while the greeting is playing: sign-in flips auth status
// synchronously, which would otherwise unmount the login page (and the greeting) instantly. While
// `playing` is true the user stays on the login route — same grid, same page — and the greeting
// navigates explicitly to the existing destination when it finishes.

interface Greeting {
  playing: boolean;
  play: () => void;
  stop: () => void;
}

const GreetingContext = createContext<Greeting | null>(null);

export function GreetingProvider({ children }: { children: ReactNode }) {
  const [playing, setPlaying] = useState(false);
  const play = useCallback(() => setPlaying(true), []);
  const stop = useCallback(() => setPlaying(false), []);
  const value = useMemo(() => ({ playing, play, stop }), [playing, play, stop]);
  return <GreetingContext.Provider value={value}>{children}</GreetingContext.Provider>;
}

export function useGreeting(): Greeting {
  const value = useContext(GreetingContext);
  if (!value) throw new Error("useGreeting must be used within a GreetingProvider");
  return value;
}
