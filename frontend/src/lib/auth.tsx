import { useQuery, useQueryClient } from "@tanstack/react-query";
import * as React from "react";

import { api } from "./api";
import type { Me } from "./types";

export function useMe() {
  return useQuery<Me>({
    queryKey: ["me"],
    queryFn: api.me,
    staleTime: 60_000,
    retry: false,
  });
}

export function useLogout() {
  const qc = useQueryClient();
  return async () => {
    await api.logout();
    qc.clear();
    window.location.href = "/login";
  };
}

/** Защищённый маршрут: показывает контент только авторизованным. */
export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { data, isLoading, isError } = useMe();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center text-muted-foreground">Загрузка…</div>
    );
  }

  if (isError || !data?.authenticated) {
    window.location.href = "/login";
    return null;
  }

  return <>{children}</>;
}
