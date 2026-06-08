import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Check, ExternalLink, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { AppHeader } from "@/components/AppHeader";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { Label, Select, Skeleton, Spinner } from "@/components/ui/misc";
import { api } from "@/lib/api";
import type { TitleDetail, UserState } from "@/lib/types";
import { formatDuration } from "@/lib/utils";

const STATUSES = [
  { value: "planned", label: "Запланировано" },
  { value: "watching", label: "Смотрю" },
  { value: "completed", label: "Просмотрено" },
  { value: "dropped", label: "Заброшено" },
  { value: "on_hold", label: "На паузе" },
];

export default function TitleDetailPage() {
  const { id } = useParams();
  const titleId = Number(id);
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data: title, isLoading } = useQuery<TitleDetail>({
    queryKey: ["title", titleId],
    queryFn: () => api.titleDetail(titleId),
  });

  if (isLoading || !title) {
    return (
      <div className="min-h-screen">
        <AppHeader />
        <div className="mx-auto max-w-[1100px] space-y-4 px-4 py-6">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <AppHeader />
      <main className="mx-auto max-w-[1100px] space-y-6 px-4 py-6 md:px-6">
        <Button variant="ghost" size="sm" onClick={() => navigate("/")} className="text-muted-foreground">
          <ArrowLeft className="size-4" />
          К библиотеке
        </Button>

        <Hero title={title} />

        <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
          <div className="space-y-6">
            {title.description && (
              <Card>
                <CardContent className="prose prose-invert pt-6 text-sm leading-relaxed text-foreground/90">
                  {title.description}
                </CardContent>
              </Card>
            )}
            {title.is_series && <Seasons title={title} />}
          </div>

          <div className="space-y-6">
            <StateEditor title={title} />
            <RemoveCard
              titleId={titleId}
              onRemoved={() => {
                qc.invalidateQueries({ queryKey: ["titles"] });
                qc.invalidateQueries({ queryKey: ["stats"] });
                navigate("/");
              }}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

function Hero({ title }: { title: TitleDetail }) {
  return (
    <div className="relative overflow-hidden rounded-xl border border-border">
      {title.cover_url && (
        <div
          className="absolute inset-0 bg-cover bg-center opacity-20 blur-sm"
          style={{ backgroundImage: `url(${title.cover_url})` }}
        />
      )}
      <div className="relative flex flex-col gap-5 p-5 sm:flex-row sm:p-6">
        <div className="h-56 w-36 shrink-0 overflow-hidden rounded-lg bg-muted shadow-lg">
          {title.poster_url && <img src={title.poster_url} alt="" className="h-full w-full object-cover" />}
        </div>
        <div className="min-w-0 space-y-3">
          <div>
            <h1 className="text-2xl font-bold leading-tight">{title.name}</h1>
            {title.original_name && title.original_name !== title.name && (
              <p className="text-muted-foreground">{title.original_name}</p>
            )}
            {title.slogan && <p className="mt-1 text-sm italic text-muted-foreground">«{title.slogan}»</p>}
          </div>

          <div className="flex flex-wrap items-center gap-2 text-sm">
            <Badge>{title.category_display}</Badge>
            {title.year && <Badge variant="muted">{title.year}</Badge>}
            {title.duration_min && <Badge variant="muted">{formatDuration(title.duration_min)}</Badge>}
            {title.age_limit && <Badge variant="outline">{title.age_limit.replace("age", "")}+</Badge>}
            {title.rating_kp != null && <span className="text-amber-300">КП ★ {title.rating_kp}</span>}
            {title.rating_imdb != null && <span className="text-amber-300">IMDb ★ {title.rating_imdb}</span>}
          </div>

          {title.genres.length > 0 && (
            <div className="text-sm text-muted-foreground">{title.genres.join(", ")}</div>
          )}
          {title.countries.length > 0 && (
            <div className="text-sm text-muted-foreground">{title.countries.join(", ")}</div>
          )}

          {title.kp_url && (
            <a
              href={title.kp_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
            >
              КиноПоиск <ExternalLink className="size-3.5" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

function StateEditor({ title }: { title: TitleDetail }) {
  const qc = useQueryClient();
  const s = title.user_state;
  const [status, setStatus] = useState(s?.status ?? "planned");
  const [rating, setRating] = useState<string>(s?.rating != null ? String(s.rating) : "");
  const [review, setReview] = useState(s?.review ?? "");
  const [startedAt, setStartedAt] = useState(s?.started_at ?? "");
  const [finishedAt, setFinishedAt] = useState(s?.finished_at ?? "");

  const mutation = useMutation({
    mutationFn: (payload: Partial<UserState>) => api.updateState(title.id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["title", title.id] });
      qc.invalidateQueries({ queryKey: ["stats"] });
      qc.invalidateQueries({ queryKey: ["titles"] });
    },
  });

  function save(e: React.FormEvent) {
    e.preventDefault();
    mutation.mutate({
      status,
      rating: rating === "" ? null : Number(rating),
      review,
      started_at: startedAt || null,
      finished_at: finishedAt || null,
    });
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <h3 className="mb-4 font-semibold">Моя отметка</h3>
        <form onSubmit={save} className="space-y-3">
          <div className="space-y-1.5">
            <Label>Статус</Label>
            <Select value={status} onChange={(e) => setStatus(e.target.value)}>
              {STATUSES.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label>Оценка (0–10)</Label>
            <Input
              type="number"
              min={0}
              max={10}
              value={rating}
              onChange={(e) => setRating(e.target.value)}
              placeholder="—"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1.5">
              <Label>Начато</Label>
              <Input type="date" value={startedAt ?? ""} onChange={(e) => setStartedAt(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label>Завершено</Label>
              <Input type="date" value={finishedAt ?? ""} onChange={(e) => setFinishedAt(e.target.value)} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label>Отзыв</Label>
            <Textarea value={review} onChange={(e) => setReview(e.target.value)} placeholder="Ваши впечатления…" />
          </div>
          <Button type="submit" className="w-full" disabled={mutation.isPending}>
            {mutation.isPending ? <Spinner className="size-4" /> : <Check className="size-4" />}
            Сохранить
          </Button>
          {mutation.isSuccess && <p className="text-center text-xs text-emerald-400">Сохранено</p>}
        </form>
      </CardContent>
    </Card>
  );
}

function Seasons({ title }: { title: TitleDetail }) {
  const qc = useQueryClient();
  // Локальное множество просмотренных эпизодов для мгновенного отклика.
  const [watched, setWatched] = useState<Set<number>>(new Set());

  useEffect(() => {
    const initial = new Set<number>();
    title.seasons.forEach((s) => s.episodes.forEach((ep) => ep.watched && initial.add(ep.id)));
    setWatched(initial);
  }, [title]);

  const toggle = useMutation({
    mutationFn: ({ episodeId, next }: { episodeId: number; next: boolean }) =>
      api.toggleEpisode(title.id, episodeId, next),
    onMutate: ({ episodeId, next }) => {
      setWatched((prev) => {
        const copy = new Set(prev);
        next ? copy.add(episodeId) : copy.delete(episodeId);
        return copy;
      });
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["stats"] });
      qc.invalidateQueries({ queryKey: ["titles"] });
    },
  });

  const totalWatched = watched.size;

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold">Сезоны и серии</h3>
          <span className="text-sm text-muted-foreground">
            {totalWatched} / {title.total_episodes} просмотрено
          </span>
        </div>
        <div className="space-y-5">
          {title.seasons.map((season) => (
            <div key={season.id}>
              <div className="mb-2 text-sm font-medium text-muted-foreground">Сезон {season.number}</div>
              <div className="space-y-1">
                {season.episodes.map((ep) => {
                  const isWatched = watched.has(ep.id);
                  return (
                    <button
                      key={ep.id}
                      onClick={() => toggle.mutate({ episodeId: ep.id, next: !isWatched })}
                      className="flex w-full items-center gap-3 rounded-md px-2 py-1.5 text-left text-sm transition hover:bg-accent"
                    >
                      <span
                        className={`flex size-5 shrink-0 items-center justify-center rounded border ${
                          isWatched ? "border-primary bg-primary text-primary-foreground" : "border-border"
                        }`}
                      >
                        {isWatched && <Check className="size-3.5" />}
                      </span>
                      <span className="w-12 shrink-0 text-muted-foreground">
                        S{season.number.toString().padStart(2, "0")}E{ep.number.toString().padStart(2, "0")}
                      </span>
                      <span className="min-w-0 flex-1 truncate">{ep.name || "—"}</span>
                      {ep.duration_min && (
                        <span className="shrink-0 text-xs text-muted-foreground">{ep.duration_min} мин</span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function RemoveCard({ titleId, onRemoved }: { titleId: number; onRemoved: () => void }) {
  const remove = useMutation({
    mutationFn: () => api.removeTitle(titleId),
    onSuccess: onRemoved,
  });

  return (
    <Card>
      <CardContent className="pt-6">
        <Button
          variant="destructive"
          className="w-full"
          onClick={() => {
            if (confirm("Удалить из вашей библиотеки? Метаданные сохранятся в кэше.")) remove.mutate();
          }}
          disabled={remove.isPending}
        >
          {remove.isPending ? <Spinner className="size-4" /> : <Trash2 className="size-4" />}
          Удалить из библиотеки
        </Button>
      </CardContent>
    </Card>
  );
}
