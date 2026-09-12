import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api";

export type AsyncStatus = "loading" | "success" | "error";

export interface AsyncState<T> {
  status: AsyncStatus;
  data: T | null;
  error: string | null;
  reload: () => void;
}

// Minimal data-fetching hook: run an async loader on mount (and on demand via reload),
// tracking loading / success / error so pages can render the correct global state
// (§29). Cancels stale results if the dependency changes or the component unmounts.
export function useAsync<T>(loader: () => Promise<T>, deps: unknown[] = []): AsyncState<T> {
  const [status, setStatus] = useState<AsyncStatus>("loading");
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);

  const reload = useCallback(() => setNonce((n) => n + 1), []);

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    setError(null);
    loader()
      .then((result) => {
        if (cancelled) return;
        setData(result);
        setStatus("success");
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof ApiError ? err.message : "Something went wrong.");
        setStatus("error");
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);

  return { status, data, error, reload };
}
