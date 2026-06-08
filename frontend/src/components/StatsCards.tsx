import { useQuery } from "@tanstack/react-query";
import { Eye, Film, Star } from "lucide-react";

import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/misc";
import { api } from "@/lib/api";
import type { Stats } from "@/lib/types";

function StatCard({
  icon,
  label,
  value,
  accent,
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
  accent: string;
}) {
  return (
    <Card className="flex items-center gap-4 p-5">
      <div className={`flex size-12 items-center justify-center rounded-xl ${accent}`}>{icon}</div>
      <div>
        <div className="text-2xl font-bold leading-tight">{value}</div>
        <div className="text-sm text-muted-foreground">{label}</div>
      </div>
    </Card>
  );
}

export function StatsCards() {
  const { data, isLoading } = useQuery<Stats>({ queryKey: ["stats"], queryFn: api.stats });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <Skeleton key={i} className="h-[88px]" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <StatCard
        icon={<Film className="size-6 text-primary" />}
        accent="bg-primary/10"
        label="Всего записей"
        value={data?.total ?? 0}
      />
      <StatCard
        icon={<Eye className="size-6 text-emerald-300" />}
        accent="bg-emerald-500/10"
        label="Просмотрено"
        value={data?.watched ?? 0}
      />
      <StatCard
        icon={<Star className="size-6 text-amber-300" />}
        accent="bg-amber-500/10"
        label="Средний рейтинг"
        value={data?.average_rating != null ? data.average_rating.toFixed(2) : "—"}
      />
    </div>
  );
}
