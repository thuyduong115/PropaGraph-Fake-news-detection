import { Hourglass } from "lucide-react";
import { useTranslation } from "react-i18next";

import { formatPercent, labelText } from "../lib/format";

interface Props {
  probFake: number | null;
  modelReady: boolean;
  trueLabel: string | null;
}

const R = 70;
const ARC = Math.PI * R;

/** Đồng hồ nửa vòng: xác suất lớp "fake" do model trả về. Chưa có model thì nói rõ. */
export default function PredictionGauge({ probFake, modelReady, trueLabel }: Props) {
  const { t, i18n } = useTranslation();

  if (!modelReady || probFake === null) {
    return (
      <div className="gauge gauge-empty">
        <Hourglass aria-hidden="true" size={22} />
        <div>
          <p className="gauge-title">{t("detail.modelPendingTitle")}</p>
          <p className="muted">{t("detail.modelPendingBody")}</p>
          <p>
            {t("detail.trueLabel")}: <strong>{labelText(trueLabel, t)}</strong>
          </p>
        </div>
      </div>
    );
  }

  const isFake = probFake >= 0.5;
  return (
    <div className="gauge">
      <svg
        className="gauge-chart"
        viewBox="-90 -85 180 95"
        role="img"
        aria-label={t("detail.probFake")}
      >
        <path d={`M${-R},0 A${R},${R} 0 0 1 ${R},0`} className="gauge-track" />
        <path
          d={`M${-R},0 A${R},${R} 0 0 1 ${R},0`}
          className={isFake ? "gauge-fill is-fake" : "gauge-fill"}
          strokeDasharray={`${ARC * probFake} ${ARC}`}
        />
        <text y="-12" textAnchor="middle" className="gauge-value">
          {formatPercent(probFake, i18n.language)}
        </text>
      </svg>
      <dl className="facts">
        <dt>{t("detail.probFake")}</dt>
        <dd>{formatPercent(probFake, i18n.language)}</dd>
        <dt>{t("detail.trueLabel")}</dt>
        <dd>{labelText(trueLabel, t)}</dd>
      </dl>
    </div>
  );
}
