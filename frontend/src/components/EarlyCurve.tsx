import { useTranslation } from "react-i18next";

import type { TimelinePoint } from "../api/types";
import { formatCutoff, formatInt, formatPercent } from "../lib/format";

interface Props {
  points: TimelinePoint[];
  index: number;
  total: number;
  modelReady: boolean;
}

const W = 320;
const H = 160;
const PAD = { l: 40, r: 12, t: 12, b: 28 };

/**
 * Đường theo mốc thời gian: xác suất fake khi có model; khi chưa có model, vẽ số node quan sát
 * (cây "lớn dần") để thanh trượt vẫn có ý nghĩa.
 */
export default function EarlyCurve({ points, index, total, modelReady }: Props) {
  const { t, i18n } = useTranslation();
  const showProb = modelReady && points.every((p) => p.prob_fake !== null);
  const values = points.map((p) => (showProb ? p.prob_fake! : p.n_nodes_used / Math.max(1, total)));
  const iw = W - PAD.l - PAD.r;
  const ih = H - PAD.t - PAD.b;
  const x = (i: number) => PAD.l + (i / Math.max(1, points.length - 1)) * iw;
  const y = (v: number) => PAD.t + (1 - v) * ih;
  const line = values.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`);
  const yLabel = (v: number) =>
    showProb ? formatPercent(v, i18n.language) : formatInt(Math.round(v * total), i18n.language);

  return (
    <figure className="curve">
      <figcaption>{showProb ? t("detail.curveProb") : t("detail.curveNodes")}</figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={t("detail.curveAria")}>
        {[0, 0.5, 1].map((v) => (
          <g key={v}>
            <line x1={PAD.l} x2={W - PAD.r} y1={y(v)} y2={y(v)} className="grid" />
            <text x={PAD.l - 6} y={y(v)} dy="0.32em" textAnchor="end" className="axis">
              {yLabel(v)}
            </text>
          </g>
        ))}
        {showProb && (
          <line x1={PAD.l} x2={W - PAD.r} y1={y(0.5)} y2={y(0.5)} className="threshold" />
        )}
        <path d={line.join("")} className="curve-line" />
        {values.map((v, i) => (
          <circle
            key={i}
            cx={x(i)}
            cy={y(v)}
            r={i === index ? 5 : 2.5}
            className={i === index ? "curve-dot is-active" : "curve-dot"}
          >
            <title>
              {formatCutoff(points[i].cutoff_h, t, i18n.language)}: {yLabel(v)}
            </title>
          </circle>
        ))}
        <text x={PAD.l} y={H - 8} className="axis">
          {formatCutoff(points[0].cutoff_h, t, i18n.language)}
        </text>
        <text x={W - PAD.r} y={H - 8} textAnchor="end" className="axis">
          {formatCutoff(points[points.length - 1].cutoff_h, t, i18n.language)}
        </text>
      </svg>
    </figure>
  );
}
