import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Plus, Search } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/misc";
import { api } from "@/lib/api";
import type { SearchResult } from "@/lib/types";

function useDebounced<T>(value: T, delay = 350): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

export function AddDialog() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [added, setAdded] = useState<Set<number>>(new Set());
  const debouncedQuery = useDebounced(query);
  const qc = useQueryClient();

  // Если введено чистое число — считаем это KP ID.
  const numericId = /^\d+$/.test(query.trim()) ? Number(query.trim()) : null;

  const { data, isFetching } = useQuery({
    queryKey: ["search", debouncedQuery],
    queryFn: () => api.search(debouncedQuery),
    enabled: open && debouncedQuery.trim().length >= 2 && numericId === null,
    staleTime: 60_000,
  });

  const addMutation = useMutation({
    mutationFn: (sourceId: number) => api.addTitle(sourceId),
    onSuccess: (_res, sourceId) => {
      setAdded((prev) => new Set(prev).add(sourceId));
      // Импорт асинхронный (Celery) — обновим список с задержкой.
      setTimeout(() => {
        qc.invalidateQueries({ queryKey: ["titles"] });
        qc.invalidateQueries({ queryKey: ["stats"] });
      }, 2500);
    },
  });

  function reset() {
    setQuery("");
    setAdded(new Set());
  }

  const results: SearchResult[] = data?.results ?? [];

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        setOpen(o);
        if (!o) reset();
      }}
    >
      <DialogTrigger asChild>
        <Button>
          <Plus className="size-4" />
          Добавить
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold">Добавить в библиотеку</DialogTitle>
          <p className="text-sm text-muted-foreground">
            Введите название для поиска или вставьте ID КиноПоиска.
          </p>
        </DialogHeader>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Например: Матрица или 301"
            className="pl-9"
          />
        </div>

        {numericId !== null && (
          <button
            onClick={() => addMutation.mutate(numericId)}
            disabled={added.has(numericId)}
            className="flex items-center justify-between rounded-md border border-border bg-accent/40 p-3 text-left transition hover:bg-accent"
          >
            <span className="text-sm">
              Добавить по ID КиноПоиска: <span className="font-semibold">{numericId}</span>
            </span>
            {added.has(numericId) ? <Check className="size-4 text-emerald-400" /> : <Plus className="size-4" />}
          </button>
        )}

        <div className="max-h-[50vh] space-y-1 overflow-y-auto">
          {isFetching && (
            <div className="flex items-center gap-2 p-3 text-sm text-muted-foreground">
              <Spinner className="size-4" /> Поиск…
            </div>
          )}
          {!isFetching && numericId === null && debouncedQuery.trim().length >= 2 && results.length === 0 && (
            <p className="p-3 text-sm text-muted-foreground">Ничего не найдено</p>
          )}
          {results.map((r) => {
            const isAdded = added.has(r.external_id);
            return (
              <div
                key={r.external_id}
                className="flex items-center gap-3 rounded-md p-2 transition hover:bg-accent"
              >
                <div className="h-16 w-11 shrink-0 overflow-hidden rounded bg-muted">
                  {r.poster_url && (
                    <img src={r.poster_url} alt="" className="h-full w-full object-cover" loading="lazy" />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-medium">{r.name}</div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    {r.year && <span>{r.year}</span>}
                    {r.is_series && <Badge variant="muted">сериал</Badge>}
                    {r.rating != null && <span className="text-amber-300">★ {r.rating}</span>}
                  </div>
                </div>
                <Button
                  size="sm"
                  variant={isAdded ? "secondary" : "outline"}
                  disabled={isAdded}
                  onClick={() => addMutation.mutate(r.external_id)}
                >
                  {isAdded ? <Check className="size-4" /> : <Plus className="size-4" />}
                  {isAdded ? "Добавлено" : "Добавить"}
                </Button>
              </div>
            );
          })}
        </div>

        {added.size > 0 && (
          <p className="text-xs text-muted-foreground">
            Импорт выполняется в фоне — записи появятся в библиотеке через несколько секунд.
          </p>
        )}
      </DialogContent>
    </Dialog>
  );
}
