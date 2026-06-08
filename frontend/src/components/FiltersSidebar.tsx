import { SlidersHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Sheet, SheetClose, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";
import type { FilterOption, Stats } from "@/lib/types";

interface Props {
  categories: FilterOption[];
  statuses: FilterOption[];
  category: string;
  status: string;
  stats?: Stats;
  onChange: (next: { category?: string; status?: string }) => void;
}

function FilterRow({
  active,
  label,
  count,
  onClick,
}: {
  active: boolean;
  label: string;
  count?: number;
  onClick: () => void;
}) {
  return (
    <SheetClose asChild>
      <button
        onClick={onClick}
        className={cn(
          "flex w-full items-center justify-between rounded-md px-3 py-2 text-sm transition",
          active ? "bg-primary/15 text-primary" : "hover:bg-accent text-foreground",
        )}
      >
        <span>{label}</span>
        {count != null && <span className="text-xs text-muted-foreground">{count}</span>}
      </button>
    </SheetClose>
  );
}

export function FiltersSidebar({ categories, statuses, category, status, stats, onChange }: Props) {
  const activeCount = (category ? 1 : 0) + (status ? 1 : 0);

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline">
          <SlidersHorizontal className="size-4" />
          Фильтры
          {activeCount > 0 && (
            <span className="ml-1 inline-flex size-5 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
              {activeCount}
            </span>
          )}
        </Button>
      </SheetTrigger>
      <SheetContent side="left">
        <SheetTitle className="text-lg font-semibold">Фильтры</SheetTitle>

        <div className="space-y-6 overflow-y-auto">
          <div>
            <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Категории
            </div>
            <div className="space-y-1">
              <FilterRow active={!category} label="Все" onClick={() => onChange({ category: "" })} />
              {categories.map((c) => (
                <FilterRow
                  key={c.value}
                  active={category === c.value}
                  label={c.label}
                  count={stats?.by_category?.[c.value]}
                  onClick={() => onChange({ category: c.value })}
                />
              ))}
            </div>
          </div>

          <div>
            <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Статус просмотра
            </div>
            <div className="space-y-1">
              <FilterRow active={!status} label="Любой" onClick={() => onChange({ status: "" })} />
              {statuses.map((s) => (
                <FilterRow
                  key={s.value}
                  active={status === s.value}
                  label={s.label}
                  count={stats?.by_status?.[s.value]}
                  onClick={() => onChange({ status: s.value })}
                />
              ))}
            </div>
          </div>

          {activeCount > 0 && (
            <SheetClose asChild>
              <Button variant="ghost" className="w-full" onClick={() => onChange({ category: "", status: "" })}>
                Сбросить фильтры
              </Button>
            </SheetClose>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
