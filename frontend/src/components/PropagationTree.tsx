import { memo, useMemo } from "react";
import { useTranslation } from "react-i18next";

import type { TreeNode } from "../api/types";
import { formatHours } from "../lib/format";
import { timeBucket } from "../lib/timeScale";
import { isVisible, layoutTree } from "../lib/tree";

interface Props {
  nodes: TreeNode[];
  edges: [number, number][];
  cutoff: number | null;
}

/**
 * Cây lan truyền dạng radial (SVG). Bố cục tính một lần cho mỗi đồ thị; kéo thanh thời gian
 * chỉ đổi class mờ/hiện, không tính lại bố cục.
 */
function PropagationTree({ nodes, edges, cutoff }: Props) {
  const { t, i18n } = useTranslation();
  const layout = useMemo(() => layoutTree(nodes, edges), [nodes, edges]);
  const tById = useMemo(() => new Map(layout.nodes.map((n) => [n.id, n])), [layout]);
  const pad = 24;
  const size = layout.radius + pad;
  const visible = layout.nodes.filter((n) => isVisible(n.t, n.isRoot, cutoff)).length;

  return (
    <svg
      className="tree"
      viewBox={`${-size} ${-size} ${size * 2} ${size * 2}`}
      role="img"
      aria-label={t("tree.aria", { visible, total: layout.nodes.length })}
    >
      <g className="tree-edges">
        {layout.edges.map((e) => {
          const target = tById.get(e.target)!;
          const on = isVisible(target.t, target.isRoot, cutoff);
          return <path key={e.target} d={e.path} className={on ? "edge" : "edge is-hidden"} />;
        })}
      </g>
      <g>
        {layout.nodes.map((n) => {
          const on = isVisible(n.t, n.isRoot, cutoff);
          const cls = n.isRoot ? "node node-root" : `node t${timeBucket(n.t)}`;
          return (
            <circle key={n.id} cx={n.x} cy={n.y} r={n.r} className={on ? cls : `${cls} is-hidden`}>
              <title>
                {n.isRoot
                  ? t("tree.rootTitle")
                  : t("tree.nodeTitle", {
                      id: n.id,
                      depth: n.depth,
                      time: formatHours(n.t, t, i18n.language),
                      degree: n.degree,
                    })}
              </title>
            </circle>
          );
        })}
      </g>
    </svg>
  );
}

export default memo(PropagationTree);
