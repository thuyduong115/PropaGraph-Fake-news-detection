import { hierarchy, tree, type HierarchyPointNode } from "d3-hierarchy";

import type { TreeNode } from "../api/types";

interface Datum {
  id: number;
  node: TreeNode;
  children: Datum[];
}

export interface PlacedNode {
  id: number;
  x: number;
  y: number;
  r: number;
  t: number | null;
  depth: number;
  degree: number;
  isRoot: boolean;
}

export interface PlacedEdge {
  source: number;
  target: number;
  path: string;
}

export interface TreeLayout {
  nodes: PlacedNode[];
  edges: PlacedEdge[];
  radius: number;
  maxT: number;
}

/**
 * Bố cục radial: gốc (bài báo) ở giữa, mỗi vòng là một mức độ sâu.
 * Node không có cha trong danh sách cạnh được treo vào gốc để vẫn hiện (giống `keep_nodes`).
 */
export function layoutTree(nodes: TreeNode[], edges: [number, number][]): TreeLayout {
  const byId = new Map<number, Datum>();
  for (const n of nodes) byId.set(n.id, { id: n.id, node: n, children: [] });
  const rootNode = nodes.find((n) => n.depth === 0) ?? nodes[0];
  const root = byId.get(rootNode.id)!;

  const hasParent = new Set<number>();
  const degree = new Map<number, number>();
  for (const [src, dst] of edges) {
    const parent = byId.get(src);
    const child = byId.get(dst);
    if (!parent || !child || hasParent.has(dst) || dst === root.id) continue;
    parent.children.push(child);
    hasParent.add(dst);
    degree.set(src, (degree.get(src) ?? 0) + 1);
  }
  for (const d of byId.values()) {
    if (d !== root && !hasParent.has(d.id)) {
      root.children.push(d);
      degree.set(root.id, (degree.get(root.id) ?? 0) + 1);
    }
  }

  const h = hierarchy(root, (d) => d.children);
  // con sớm nằm trước: các nhánh xếp theo thời gian quanh vòng
  h.sort((a, b) => (a.data.node.t_rel_h ?? 0) - (b.data.node.t_rel_h ?? 0));
  const levels = Math.max(1, h.height);
  const radius = 60 + levels * 70;
  const placed = tree<Datum>()
    .size([2 * Math.PI, radius])
    .separation((a, b) => (a.parent === b.parent ? 1 : 2) / Math.max(1, a.depth))(h);

  const point = (n: HierarchyPointNode<Datum>): [number, number] => {
    const angle = n.x - Math.PI / 2;
    return [n.y * Math.cos(angle), n.y * Math.sin(angle)];
  };

  let maxT = 0;
  const out: PlacedNode[] = [];
  const outEdges: PlacedEdge[] = [];
  for (const n of placed.descendants()) {
    const [x, y] = point(n);
    const deg = degree.get(n.data.id) ?? 0;
    const t = n.data.node.t_rel_h;
    if (t !== null && t > maxT) maxT = t;
    const isRoot = n.data.id === root.id;
    out.push({
      id: n.data.id,
      x,
      y,
      r: isRoot ? 11 : 2.5 + Math.min(7, Math.sqrt(deg) * 1.4),
      t: isRoot ? 0 : t,
      depth: n.data.node.depth,
      degree: deg,
      isRoot,
    });
    if (n.parent) {
      const [px, py] = point(n.parent);
      outEdges.push({
        source: n.parent.data.id,
        target: n.data.id,
        path: `M${px.toFixed(1)},${py.toFixed(1)}L${x.toFixed(1)},${y.toFixed(1)}`,
      });
    }
  }
  return { nodes: out, edges: outEdges, radius, maxT };
}

/** Node hiện ở mốc `cutoff` (null = toàn bộ): gốc luôn hiện. */
export function isVisible(t: number | null, isRoot: boolean, cutoff: number | null): boolean {
  if (isRoot || cutoff === null) return true;
  return t !== null && t <= cutoff;
}
