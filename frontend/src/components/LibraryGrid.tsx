import { useNavigate } from "react-router-dom";

import { StatusBadge } from "@/components/ui/badge";
import type { TitleRow } from "@/lib/types";

export function LibraryGrid({ rows }: { rows: TitleRow[] }) {
  const navigate = useNavigate();
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {rows.map((t) => (
        <button
          key={t.id}
          onClick={() => navigate(`/title/${t.id}`)}
          className="group overflow-hidden rounded-lg border border-border bg-card text-left transition hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg"
        >
          <div className="aspect-[2/3] overflow-hidden bg-muted">
            {t.poster_url ? (
              <img
                src={t.poster_url}
                alt={t.name}
                loading="lazy"
                className="h-full w-full object-cover transition group-hover:scale-105"
              />
            ) : (
              <div className="flex h-full items-center justify-center text-muted-foreground">нет постера</div>
            )}
          </div>
          <div className="space-y-2 p-3">
            <div className="line-clamp-2 min-h-[2.5em] text-sm font-medium leading-tight">{t.name}</div>
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>{t.year ?? ""}</span>
              {t.rating_kp != null && <span className="text-amber-300">★ {t.rating_kp}</span>}
            </div>
            <div className="flex items-center justify-between">
              <StatusBadge status={t.user_status} label={t.user_status_display} />
              {t.progress_label && <span className="text-xs text-muted-foreground">{t.progress_label}</span>}
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
