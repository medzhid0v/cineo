import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, LayoutGrid, Search, Table2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { AppHeader } from "@/components/AppHeader";
import { ColumnsMenu } from "@/components/ColumnsMenu";
import { FiltersSidebar } from "@/components/FiltersSidebar";
import { LibraryGrid } from "@/components/LibraryGrid";
import { LibraryTable } from "@/components/LibraryTable";
import { StatsCards } from "@/components/StatsCards";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/misc";
import { api } from "@/lib/api";
import type { Preferences, Stats, TitlesResponse } from "@/lib/types";
import { cn } from "@/lib/utils";

export default function LibraryPage() {
  const qc = useQueryClient();
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  const [q, setQ] = useState("");
  const [debouncedQ, setDebouncedQ] = useState("");
  const [page, setPage] = useState(1);

  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(q), 300);
    return () => clearTimeout(t);
  }, [q]);

  useEffect(() => setPage(1), [category, status, debouncedQ]);

  const { data: prefs } = useQuery<Preferences>({ queryKey: ["preferences"], queryFn: api.preferences });
  const { data: stats } = useQuery<Stats>({ queryKey: ["stats"], queryFn: api.stats });

  const pageSize = prefs?.page_size ?? 50;
  const viewMode = prefs?.view_mode ?? "table";
  const visibleColumns = prefs?.visible_columns ?? [];

  const { data, isLoading, isFetching } = useQuery<TitlesResponse>({
    queryKey: ["titles", { category, status, q: debouncedQ, page, pageSize }],
    queryFn: () => api.titles({ category, status, q: debouncedQ, page, page_size: pageSize }),
    placeholderData: keepPreviousData,
  });

  const savePrefs = useMutation({
    mutationFn: (payload: Partial<Preferences>) => api.savePreferences(payload),
    onSuccess: (next) => qc.setQueryData(["preferences"], next),
  });

  const columnLabels = useMemo(() => {
    const map: Record<string, string> = {};
    prefs?.available_columns.forEach((c) => (map[c.key] = c.label));
    return map;
  }, [prefs]);

  const totalPages = data ? Math.max(1, Math.ceil(data.count / pageSize)) : 1;
  const rows = data?.results ?? [];
  const filters = data?.filters;

  function setView(mode: "table" | "grid") {
    savePrefs.mutate({ view_mode: mode });
  }

  return (
    <div className="min-h-screen">
      <AppHeader />
      <main className="mx-auto max-w-[1400px] space-y-6 px-4 py-6 md:px-6">
        <StatsCards />

        {/* Тулбар */}
        <div className="flex flex-wrap items-center gap-2">
          {filters && (
            <FiltersSidebar
              categories={filters.categories}
              statuses={filters.statuses}
              category={category}
              status={status}
              stats={stats}
              onChange={(next) => {
                if (next.category !== undefined) setCategory(next.category);
                if (next.status !== undefined) setStatus(next.status);
              }}
            />
          )}

          <div className="relative min-w-[200px] flex-1">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Поиск по библиотеке…"
              className="pl-9"
            />
          </div>

          <div className="flex items-center rounded-md border border-border p-0.5">
            <button
              onClick={() => setView("table")}
              className={cn(
                "flex size-8 items-center justify-center rounded transition",
                viewMode === "table" ? "bg-accent text-foreground" : "text-muted-foreground hover:text-foreground",
              )}
              title="Таблица"
            >
              <Table2 className="size-4" />
            </button>
            <button
              onClick={() => setView("grid")}
              className={cn(
                "flex size-8 items-center justify-center rounded transition",
                viewMode === "grid" ? "bg-accent text-foreground" : "text-muted-foreground hover:text-foreground",
              )}
              title="Сетка"
            >
              <LayoutGrid className="size-4" />
            </button>
          </div>

          {viewMode === "table" && prefs && (
            <ColumnsMenu
              available={prefs.available_columns}
              visible={visibleColumns}
              defaults={prefs.default_columns}
              onChange={(next) => savePrefs.mutate({ visible_columns: next })}
            />
          )}
        </div>

        {/* Контент */}
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-14" />
            ))}
          </div>
        ) : rows.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border p-12 text-center text-muted-foreground">
            <p className="mb-1 text-lg font-medium text-foreground">Пока пусто</p>
            <p>Нажмите «Добавить», чтобы найти фильм или сериал и добавить его в библиотеку.</p>
          </div>
        ) : viewMode === "table" ? (
          <LibraryTable rows={rows} visibleColumns={visibleColumns} columnLabels={columnLabels} />
        ) : (
          <LibraryGrid rows={rows} />
        )}

        {/* Пагинация */}
        {data && data.count > pageSize && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              Показано {rows.length} из {data.count} {isFetching && "· обновление…"}
            </span>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                <ChevronLeft className="size-4" />
                Назад
              </Button>
              <span className="text-sm text-muted-foreground">
                {page} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Вперёд
                <ChevronRight className="size-4" />
              </Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
