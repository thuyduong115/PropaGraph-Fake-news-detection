import { useMemo } from "react";
import { useTranslation } from "react-i18next";

import type { TableInfo } from "../api/types";
import { useApi } from "../api/useApi";
import ResultTable from "../components/ResultTable";
import { StateView } from "../components/StateView";
import reliabilityMd from "../content/data_reliability.md?raw";
import { parseSections, sectionFor } from "../lib/markdown";

const TOPICS = ["labels", "nodeOrder", "timeNoise", "gossipcopIds", "duplicateTitles", "rootUser"];

export default function DataReliability() {
  const { t } = useTranslation();
  const tables = useApi<TableInfo[]>("/results/tables?group=reliability");
  const sections = useMemo(() => parseSections(reliabilityMd), []);

  return (
    <section>
      <header className="page-head">
        <h1>{t("reliability.title")}</h1>
        <p className="muted lead">{t("reliability.lead")}</p>
      </header>
      <section className="result-block">
        <h2>{t("reliability.topicsTitle")}</h2>
        <ul className="topics">
          {TOPICS.map((k) => (
            <li key={k}>
              <strong>{t(`reliability.topics.${k}`)}</strong>
              {sectionFor(sections, k).map((p, i) => (
                <p key={i}>{p}</p>
              ))}
            </li>
          ))}
        </ul>
      </section>
      <StateView
        loading={tables.loading}
        error={tables.error}
        onRetry={tables.reload}
        empty={tables.data?.length === 0}
        emptyText={t("reliability.empty")}
      >
        {tables.data?.map((x) => (
          <ResultTable key={x.name} name={x.name} notes={sectionFor(sections, x.name)} />
        ))}
      </StateView>
    </section>
  );
}
