import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useParams } from "react-router-dom";

import type { Feature, GraphDetail as Detail, Timeline } from "../api/types";
import { useApi } from "../api/useApi";
import EarlyCurve from "../components/EarlyCurve";
import PredictionGauge from "../components/PredictionGauge";
import PropagationTree from "../components/PropagationTree";
import Segmented from "../components/Segmented";
import { StateView } from "../components/StateView";
import TimeLegend from "../components/TimeLegend";
import TimeSlider from "../components/TimeSlider";
import { datasetText, formatHours, formatInt, labelText } from "../lib/format";

export default function GraphDetail() {
  const { t, i18n } = useTranslation();
  const { ds = "", gid = "" } = useParams();
  const [feature, setFeature] = useState<Feature>("bert");
  const detail = useApi<Detail>(`/datasets/${ds}/graphs/${gid}`);
  // một lần gọi cho cả thanh trượt (mỗi đặc trưng một lần, có cache)
  const timeline = useApi<Timeline>(`/datasets/${ds}/graphs/${gid}/timeline?feature=${feature}`);
  const [index, setIndex] = useState<number | null>(null);

  const points = timeline.data?.points ?? [];
  const current = index ?? Math.max(0, points.length - 1);
  const cutoff = points[current]?.cutoff_h ?? null;
  const g = detail.data;

  return (
    <section>
      <Link to={`/?ds=${ds}`} className="back">
        <ArrowLeft size={16} aria-hidden="true" />
        {t("detail.back")}
      </Link>
      <StateView loading={detail.loading} error={detail.error} onRetry={detail.reload}>
        {g && (
          <>
            <header className="page-head">
              <h1>{g.title || t("explorer.untitled", { id: g.news_id ?? g.gid })}</h1>
              <p className="muted">
                {[datasetText(g.dataset, t), `gid ${g.gid}`, g.news_id].filter(Boolean).join(", ")}
              </p>
            </header>
            <div className="detail">
              <div className="detail-main">
                <div className="tree-frame">
                  <PropagationTree nodes={g.nodes} edges={g.edges} cutoff={cutoff} />
                </div>
                <TimeLegend />
                <StateView
                  loading={timeline.loading && !timeline.data}
                  error={timeline.error}
                  onRetry={timeline.reload}
                >
                  {points.length > 0 && (
                    <TimeSlider
                      points={points}
                      index={current}
                      total={g.n_nodes}
                      onChange={setIndex}
                    />
                  )}
                </StateView>
              </div>
              <aside className="detail-side" aria-label={t("detail.panel")}>
                <Segmented
                  label={t("detail.feature")}
                  value={feature}
                  options={[
                    { value: "profile", label: t("features.profile") },
                    { value: "bert", label: t("features.bert") },
                  ]}
                  onChange={setFeature}
                />
                <PredictionGauge
                  probFake={points[current]?.prob_fake ?? null}
                  modelReady={timeline.data?.model_ready ?? false}
                  trueLabel={g.label}
                />
                {points.length > 0 && (
                  <EarlyCurve
                    points={points}
                    index={current}
                    total={g.n_nodes}
                    modelReady={timeline.data?.model_ready ?? false}
                  />
                )}
                <dl className="facts">
                  <dt>{t("detail.trueLabel")}</dt>
                  <dd>{labelText(g.label, t)}</dd>
                  <dt>{t("detail.nodes")}</dt>
                  <dd>{formatInt(g.n_nodes, i18n.language)}</dd>
                  <dt>{t("detail.depth")}</dt>
                  <dd>{g.depth}</dd>
                  <dt>{t("detail.span")}</dt>
                  <dd>{formatHours(g.span_h, t, i18n.language)}</dd>
                  <dt>{t("detail.newsId")}</dt>
                  <dd>{g.news_id ?? t("labels.unknown")}</dd>
                </dl>
              </aside>
            </div>
          </>
        )}
      </StateView>
    </section>
  );
}
