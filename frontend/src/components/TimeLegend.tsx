import { useTranslation } from "react-i18next";

import { formatHours } from "../lib/format";
import { TIME_STOPS_H } from "../lib/timeScale";

/** Chú giải thang màu thời gian và kích thước node. */
export default function TimeLegend() {
  const { t, i18n } = useTranslation();
  return (
    <div className="legend" aria-label={t("tree.legend")}>
      <span className="legend-item">
        <svg width="18" height="18" aria-hidden="true">
          <circle cx="9" cy="9" r="7" className="node node-root" />
        </svg>
        {t("tree.legendRoot")}
      </span>
      <span className="legend-item">
        {t("tree.legendTime")}
        <span className="legend-scale" aria-hidden="true">
          {TIME_STOPS_H.map((_, i) => (
            <span key={i} className={`swatch t${i}`} />
          ))}
        </span>
        <span className="legend-range">
          {formatHours(TIME_STOPS_H[0], t, i18n.language)} →{" "}
          {formatHours(TIME_STOPS_H[TIME_STOPS_H.length - 1], t, i18n.language)}
        </span>
      </span>
      <span className="legend-item muted">{t("tree.legendSize")}</span>
    </div>
  );
}
