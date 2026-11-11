// Kiểu dữ liệu khớp backend/app/schemas. Khi API ổn định: `npm run gen:api` sinh schema.d.ts.

export type Feature = "profile" | "bert";
export type DatasetName = "politifact" | "gossipcop";

export interface Health {
  status: "ok" | "degraded";
  version: string;
  models_loaded: string[];
  synthetic: boolean;
  auth_required: boolean;
  problems: string[];
  notes: string[];
}

export interface Me {
  username: string;
  role: "admin" | "user";
  auth_required: boolean;
}

export interface DatasetInfo {
  name: DatasetName;
  n_graphs: number;
  labels: string[];
}

export interface GraphSummary {
  gid: number;
  news_id: string | null;
  title: string | null;
  label: string | null;
  n_nodes: number;
  depth: number;
  span_h: number | null;
  growth: number[];
}

export interface GraphPage {
  dataset: DatasetName;
  total: number;
  page: number;
  size: number;
  timeline_h: (number | null)[];
  items: GraphSummary[];
}

export interface TreeNode {
  id: number;
  depth: number;
  t_rel_h: number | null;
}

export interface GraphDetail extends GraphSummary {
  dataset: DatasetName;
  nodes: TreeNode[];
  edges: [number, number][];
}

export interface TimelinePoint {
  cutoff_h: number | null;
  n_nodes_used: number;
  prob_fake: number | null;
}

export interface Timeline {
  dataset: DatasetName;
  gid: number;
  feature: Feature;
  model_ready: boolean;
  n_nodes_total: number;
  points: TimelinePoint[];
}

export interface TableInfo {
  name: string;
  group: "experiment" | "reliability" | "summary" | "meta";
  n_rows: number;
}

export interface TableData extends TableInfo {
  columns: string[];
  rows: string[][];
}

export interface FigureInfo {
  name: string;
  url: string;
}

export interface AdminStatus {
  artifacts_dir: string;
  loaded_at: number;
  synthetic: boolean;
  datasets: Record<string, number>;
  tables: string[];
  figures: number;
  model_card: boolean;
  models_loaded: string[];
  problems: string[];
  notes: string[];
}
