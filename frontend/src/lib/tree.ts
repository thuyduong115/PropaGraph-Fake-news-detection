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

// Khoảng cách tối thiểu (đơn vị viewBox) giữa hai node liền nhau trên một vòng, khoảng cách
// giữa hai vòng độ sâu, và độ lệch giữa các vòng phụ khi so le.
const NODE_GAP = 7;
const RING_GAP = 70;
const FIRST_RING = 130;
const STAGGER_STEP = 16;

/** Số vòng phụ để so le node khi một độ sâu quá đông (giữ cây gọn mà không đè node). */
function staggerOf(count: number): number {
  return count > 160 ? 3 : count > 70 ? 2 : 1;
}

/**
 * Bán kính từng độ sâu: đủ chu vi cho số node ở độ sâu đó (sau khi so le), luôn cách vòng
 * trước ít nhất RING_GAP. Trả bán kính vòng chính và số vòng phụ của mỗi độ sâu.
 */
function ringRadii(counts: number[]): { ring: number[]; stagger: number[] } {
  const ring = [0];
  const stagger = [1];
  for (let d = 1; d < counts.length; d++) {
    const st = staggerOf(counts[d]);
    const need = (counts[d] * NODE_GAP) / (2 * Math.PI * st);
    const prevOuter = ring[d - 1] + (stagger[d - 1] - 1) * STAGGER_STEP;
    ring.push(Math.max(d === 1 ? FIRST_RING : 0, prevOuter + RING_GAP, need));
    stagger.push(st);
  }
  return { ring, stagger };
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
  const placed = tree<Datum>()
    .size([2 * Math.PI, 1])
    .separation((a, b) => (a.parent === b.parent ? 1 : 2) / Math.max(1, a.depth))(h);

  // Bán kính theo số node mỗi độ sâu (thay cho bán kính cố định): cây lớn không bị dồn vòng.
  const all = placed.descendants();
  const counts = new Array<number>(h.height + 1).fill(0);
  for (const n of all) counts[n.depth] += 1;
  const { ring, stagger } = ringRadii(counts);
  const byDepth = new Map<number, HierarchyPointNode<Datum>[]>();
  for (const n of all) {
    const list = byDepth.get(n.depth);
    if (list) list.push(n);
    else byDepth.set(n.depth, [n]);
  }
  const rOf = new Map<HierarchyPointNode<Datum>, number>();
  for (const [d, ns] of byDepth) {
    ns.sort((a, b) => a.x - b.x);
    ns.forEach((n, i) => rOf.set(n, ring[d] + (i % stagger[d]) * STAGGER_STEP));
  }
  const radius = Math.max(...all.map((n) => rOf.get(n) ?? 0));

  const point = (n: HierarchyPointNode<Datum>): [number, number] => {
    const angle = n.x - Math.PI / 2;
    const r = rOf.get(n) ?? 0;
    return [r * Math.cos(angle), r * Math.sin(angle)];
  };

  let maxT = 0;
  const out: PlacedNode[] = [];
  const outEdges: PlacedEdge[] = [];
  for (const n of all) {
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
