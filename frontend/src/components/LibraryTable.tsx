import {
  type ColumnDef as TanColumnDef,
  type SortingState,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { ArrowDown, ArrowUp, ChevronsUpDown } from "lucide-react";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { StatusBadge } from "@/components/ui/badge";
import { cn, formatDate, formatDuration } from "@/lib/utils";
import type { TitleRow } from "@/lib/types";

function Rating({ value }: { value: number | null }) {
  if (value == null) return <span className="text-muted-foreground">—</span>;
  return <span className="font-medium text-amber-300">★ {value}</span>;
}

function Tags({ items }: { items: string[] }) {
  if (!items?.length) return <span className="text-muted-foreground">—</span>;
  return <span className="text-muted-foreground">{items.slice(0, 3).join(", ")}</span>;
}

// Рендереры ячеек по ключу колонки.
const CELL: Record<string, (t: TitleRow) => React.ReactNode> = {
  poster_url: (t) => (
    <div className="h-14 w-10 overflow-hidden rounded bg-muted">
      {t.poster_url && <img src={t.poster_url} alt="" className="h-full w-full object-cover" loading="lazy" />}
    </div>
  ),
  name: (t) => (
    <div className="min-w-0">
      <div className="truncate font-medium">{t.name}</div>
      {t.original_name && t.original_name !== t.name && (
        <div className="truncate text-xs text-muted-foreground">{t.original_name}</div>
      )}
    </div>
  ),
  year: (t) => t.year ?? "—",
  category_display: (t) => t.category_display,
  user_status_display: (t) => <StatusBadge status={t.user_status} label={t.user_status_display} />,
  user_rating: (t) => <Rating value={t.user_rating} />,
  rating_kp: (t) => <Rating value={t.rating_kp} />,
  rating_imdb: (t) => <Rating value={t.rating_imdb} />,
  duration_min: (t) => formatDuration(t.duration_min),
  genres: (t) => <Tags items={t.genres} />,
  countries: (t) => <Tags items={t.countries} />,
  age_limit: (t) => (t.age_limit ? t.age_limit.replace("age", "") + "+" : "—"),
  progress_label: (t) => t.progress_label ?? "—",
  last_viewed_at: (t) => formatDate(t.last_viewed_at),
};

// Ключ сортировки -> accessor.
const SORT_ACCESSOR: Record<string, (t: TitleRow) => string | number> = {
  name: (t) => t.name.toLowerCase(),
  year: (t) => t.year ?? 0,
  category_display: (t) => t.category_display,
  user_status_display: (t) => t.user_status_display ?? "",
  user_rating: (t) => t.user_rating ?? -1,
  rating_kp: (t) => t.rating_kp ?? -1,
  rating_imdb: (t) => t.rating_imdb ?? -1,
  duration_min: (t) => t.duration_min ?? -1,
  last_viewed_at: (t) => t.last_viewed_at ?? "",
};

interface Props {
  rows: TitleRow[];
  visibleColumns: string[];
  columnLabels: Record<string, string>;
}

export function LibraryTable({ rows, visibleColumns, columnLabels }: Props) {
  const navigate = useNavigate();
  const [sorting, setSorting] = useState<SortingState>([]);

  const columns = useMemo<TanColumnDef<TitleRow>[]>(
    () =>
      visibleColumns.map((key) => ({
        id: key,
        header: columnLabels[key] ?? key,
        accessorFn: SORT_ACCESSOR[key] ?? (() => ""),
        enableSorting: key in SORT_ACCESSOR,
        cell: ({ row }) => CELL[key]?.(row.original) ?? null,
      })),
    [visibleColumns, columnLabels],
  );

  const table = useReactTable({
    data: rows,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead className="border-b border-border bg-card/50">
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((header) => {
                const sortable = header.column.getCanSort();
                const sortDir = header.column.getIsSorted();
                return (
                  <th
                    key={header.id}
                    className={cn(
                      "px-4 py-3 text-left font-medium text-muted-foreground whitespace-nowrap",
                      sortable && "cursor-pointer select-none hover:text-foreground",
                    )}
                    onClick={sortable ? header.column.getToggleSortingHandler() : undefined}
                  >
                    <span className="inline-flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {sortable &&
                        (sortDir === "asc" ? (
                          <ArrowUp className="size-3" />
                        ) : sortDir === "desc" ? (
                          <ArrowDown className="size-3" />
                        ) : (
                          <ChevronsUpDown className="size-3 opacity-40" />
                        ))}
                    </span>
                  </th>
                );
              })}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr
              key={row.id}
              onClick={() => navigate(`/title/${row.original.id}`)}
              className="cursor-pointer border-b border-border/60 transition hover:bg-accent/40"
            >
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="px-4 py-2.5 align-middle">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
