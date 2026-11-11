import { useId } from "react";
import { useTranslation } from "react-i18next";

import type { TimelinePoint } from "../api/types";
import { formatCutoff, formatInt } from "../lib/format";

interface Props {
  points: TimelinePoint[];
  index: number;
  total: number;
  onChange: (index: number) => void;
}

/** Thanh trượt qua các mốc của timeline; dữ liệu mọi mốc đã có sẵn, kéo không gọi API. */
export default function TimeSlider({ points, index, total, onChange }: Props) {
  const { t, i18n } = useTranslation();
  const id = useId();
  const current = points[index];
  const label = formatCutoff(current.cutoff_h, t, i18n.language);

  return (
    <div className="slider">
      <div className="slider-head">
        <label htmlFor={id}>{t("detail.observedUntil")}</label>
        <output htmlFor={id} className="slider-value">
          <strong>{label}</strong>
          <span className="muted">
            {t("detail.nodesVisible", {
              used: formatInt(current.n_nodes_used, i18n.language),
              total: formatInt(total, i18n.language),
            })}
          </span>
        </output>
      </div>
      <input
        id={id}
        type="range"
        min={0}
        max={points.length - 1}
        step={1}
        value={index}
        aria-valuetext={label}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <div className="slider-ticks" aria-hidden="true">
        {points.map((p, i) => (
          <button
            key={i}
            type="button"
            tabIndex={-1}
            className={i === index ? "tick is-active" : "tick"}
            onClick={() => onChange(i)}
          >
            {formatCutoff(p.cutoff_h, t, i18n.language)}
          </button>
        ))}
      </div>
    </div>
  );
}
