import { useMemo } from "react";
import { useTranslation } from "react-i18next";

import type { FigureInfo, TableInfo } from "../api/types";
import { useApi } from "../api/useApi";
import ResultTable from "../components/ResultTable";
import { StateView } from "../components/StateView";
import resultsMd from "../content/results.md?raw";
import { parseSections, sectionFor } from "../lib/markdown";

export default function Results() {
  const { t } = useTranslation();
  const tables = useApi<TableInfo[]>("/results/tables");
  const figures = useApi<FigureInfo[]>("/results/figures");
  const sections = useMemo(() => parseSections(resultsMd), []);
  const shown = (tables.data ?? []).filter(
    (x) => x.group === "experiment" || x.group === "summary",
  );

  return (
    <section>
      <header className="page-head">
        <h1>{t("results.title")}</h1>
        <p className="muted lead">{t("results.lead")}</p>
      </header>
      <StateView
        loading={tables.loading}
        error={tables.error}
        onRetry={tables.reload}
        empty={shown.length === 0}
        emptyText={t("results.empty")}
      >
        {shown.map((x) => (
          <ResultTable key={x.name} name={x.name} notes={sectionFor(sections, x.name)} />
        ))}
      </StateView>
      {figures.data && figures.data.length > 0 && (
        <section className="result-block">
          <h2>{t("results.figures")}</h2>
          <div className="figures">
            {figures.data.map((f) => (
              <figure key={f.name}>
                <img src={f.url} alt={f.name} loading="lazy" />
                <figcaption>{f.name}</figcaption>
              </figure>
            ))}
          </div>
        </section>
      )}
    </section>
  );
}
