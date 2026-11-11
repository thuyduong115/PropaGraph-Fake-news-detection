import { useCallback, useEffect, useState } from "react";

import { apiGet } from "./client";

// Cache theo URL trong phiên: quay lại trang hay kéo thanh trượt không gọi lại API.
const cache = new Map<string, unknown>();

export function clearApiCache(): void {
  cache.clear();
}

export interface ApiState<T> {
  data: T | undefined;
  error: Error | undefined;
  loading: boolean;
  reload: () => void;
}

export function useApi<T>(path: string | null): ApiState<T> {
  const [state, setState] = useState<{ data?: T; error?: Error; loading: boolean }>(() => ({
    data: path ? (cache.get(path) as T | undefined) : undefined,
    loading: path !== null && !cache.has(path),
  }));
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    if (path === null) {
      setState({ loading: false });
      return;
    }
    if (cache.has(path) && nonce === 0) {
      setState({ data: cache.get(path) as T, loading: false });
      return;
    }
    let alive = true;
    setState((s) => ({ data: s.data, loading: true }));
    apiGet<T>(path)
      .then((data) => {
        cache.set(path, data);
        if (alive) setState({ data, loading: false });
      })
      .catch((error: Error) => {
        if (alive) setState({ error, loading: false });
      });
    return () => {
      alive = false;
    };
  }, [path, nonce]);

  const reload = useCallback(() => {
    if (path) cache.delete(path);
    setNonce((n) => n + 1);
  }, [path]);

  return { data: state.data, error: state.error, loading: state.loading, reload };
}
