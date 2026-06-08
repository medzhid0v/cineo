import type {
  Me,
  Preferences,
  SearchResponse,
  Stats,
  TitleDetail,
  TitlesResponse,
  UserState,
} from "./types";

const API_BASE = "/api";

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp("(^|;\\s*)" + name + "=([^;]*)"));
  return match ? decodeURIComponent(match[2]) : null;
}

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(status: number, message: string, data?: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const method = (options.method ?? "GET").toUpperCase();
  const headers = new Headers(options.headers);

  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    const csrf = getCookie("csrftoken");
    if (csrf) headers.set("X-CSRFToken", csrf);
    if (options.body && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
  }

  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "same-origin",
    ...options,
    headers,
  });

  if (res.status === 204) return undefined as T;

  let data: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const detail =
      (data && typeof data === "object" && "detail" in data && (data as { detail: string }).detail) ||
      `Ошибка запроса (${res.status})`;
    throw new ApiError(res.status, String(detail), data);
  }

  return data as T;
}

export const api = {
  // auth
  me: () => request<Me>("/me/"),
  login: (username: string, password: string) =>
    request<{ id: number; username: string }>("/auth/login/", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  signup: (username: string, password: string) =>
    request<{ id: number; username: string }>("/auth/signup/", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  logout: () => request<void>("/auth/logout/", { method: "POST" }),

  // stats
  stats: () => request<Stats>("/stats/"),

  // titles
  titles: (params: Record<string, string | number | undefined>) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "" && v !== null) qs.set(k, String(v));
    });
    const query = qs.toString();
    return request<TitlesResponse>(`/titles/${query ? `?${query}` : ""}`);
  },
  titleDetail: (id: number) => request<TitleDetail>(`/titles/${id}/`),
  addTitle: (sourceId: number) =>
    request<{ queued: boolean; source_id: number }>("/titles/add/", {
      method: "POST",
      body: JSON.stringify({ source_id: sourceId }),
    }),
  updateState: (id: number, payload: Partial<UserState>) =>
    request<UserState>(`/titles/${id}/state/`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  toggleEpisode: (id: number, episodeId: number, watched: boolean) =>
    request<{ episode_id: number; watched: boolean }>(`/titles/${id}/toggle-episode/`, {
      method: "POST",
      body: JSON.stringify({ episode_id: episodeId, watched }),
    }),
  removeTitle: (id: number) => request<void>(`/titles/${id}/remove/`, { method: "DELETE" }),

  // external search
  search: (q: string) => request<SearchResponse>(`/search/?q=${encodeURIComponent(q)}`),

  // preferences
  preferences: () => request<Preferences>("/preferences/"),
  savePreferences: (payload: Partial<Pick<Preferences, "visible_columns" | "page_size" | "view_mode">>) =>
    request<Preferences>("/preferences/", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
};
