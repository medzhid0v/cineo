export interface Me {
  authenticated: boolean;
  id?: number;
  username?: string;
  is_staff?: boolean;
}

export interface FilterOption {
  value: string;
  label: string;
}

export interface TitleRow {
  id: number;
  name: string;
  original_name: string;
  year: number | null;
  category: string;
  category_display: string;
  is_series: boolean;
  poster_url: string;
  duration_min: number | null;
  rating_kp: number | null;
  rating_imdb: number | null;
  genres: string[];
  countries: string[];
  age_limit: string;
  start_year: number | null;
  end_year: number | null;
  user_status: string | null;
  user_status_display: string | null;
  user_rating: number | null;
  progress_label: string | null;
  last_viewed_at: string | null;
  created_at: string;
}

export interface TitlesResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TitleRow[];
  filters: {
    category: string;
    status: string;
    q: string;
    categories: FilterOption[];
    statuses: FilterOption[];
  };
}

export interface Stats {
  total: number;
  watched: number;
  average_rating: number | null;
  by_category: Record<string, number>;
  by_status: Record<string, number>;
}

export interface SearchResult {
  external_id: number;
  name: string;
  year: number | null;
  poster_url: string;
  is_series: boolean;
  rating: number | null;
  description: string;
}

export interface SearchResponse {
  total: number;
  results: SearchResult[];
}

export interface Episode {
  id: number;
  number: number;
  name: string;
  duration_min: number | null;
  air_date: string | null;
  watched: boolean;
}

export interface Season {
  id: number;
  number: number;
  episodes_count: number | null;
  episodes: Episode[];
}

export interface UserState {
  status: string;
  status_display: string;
  rating: number | null;
  review: string;
  started_at: string | null;
  finished_at: string | null;
  updated_at: string;
}

export interface TitleDetail {
  id: number;
  name: string;
  original_name: string;
  year: number | null;
  category: string;
  category_display: string;
  is_series: boolean;
  poster_url: string;
  cover_url: string;
  kp_url: string;
  imdb_id: string;
  duration_min: number | null;
  rating_kp: number | null;
  rating_imdb: number | null;
  genres: string[];
  countries: string[];
  age_limit: string;
  slogan: string;
  description: string;
  short_description: string;
  start_year: number | null;
  end_year: number | null;
  seasons: Season[];
  user_state: UserState | null;
  progress: {
    current_season_number: number | null;
    current_episode_number: number | null;
    last_watched_at: string | null;
  } | null;
  total_episodes: number;
  watched_episodes: number;
}

export interface ColumnDef {
  key: string;
  label: string;
}

export interface Preferences {
  visible_columns: string[];
  page_size: number;
  view_mode: "table" | "grid";
  available_columns: ColumnDef[];
  default_columns: string[];
}
