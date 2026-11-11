import { ChevronLeft, ChevronRight, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useSearchParams } from "react-router-dom";

import { query } from "../api/client";
import type { DatasetInfo, DatasetName, GraphPage } from "../api/types";
import { useApi } from "../api/useApi";
import Segmented from "../components/Segmented";
import Sparkline from "../components/Sparkline";
import { StateView } from "../components/StateView";
import { datasetText, formatHours, formatInt, labelText } from "../lib/format";

const SIZE = 20;
const SORTS = ["gid", "-n_nodes", "n_nodes", "-depth", "-span_h"] as const;

export default function Explorer() {
  const { t, i18n } = useTranslation();
  const [params, setParams] = useSearchParams();
  const ds = (params.get("ds") as DatasetName) || "gossipcop";
  const label = params.get("label") ?? "";
  const minNodes = params.get("min") ?? "";
  const maxNodes = params.get("max") ?? "";
  const q = params.get("q") ?? "";
  const sort = params.get("sort") ?? "gid";
  const page = Number(params.get("page") ?? "1") || 1;
  const [qDraft, setQDraft] = useState(q);

  const update = (patch: Record<string, string>, resetPage = true) => {
    const next = new URLSearchParams(params);
    for (const [k, v] of Object.entries(patch)) {
      if (v) next.set(k, v);
      else next.delete(k);
    }
    if (resetPage) next.delete("page");
    setParams(next, { replace: true });
  };

  // tìm theo tiêu đề: chờ người dùng ngừng gõ rồi mới gọi API
  useEffect(() => {
    if (qDraft === q) return;
    const id = window.setTimeout(() => update({ q: qDraft }), 300);
    return () => window.clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [qDraft]);

  const datasets = useApi<DatasetInfo[]>("/datasets");
  const labels = datasets.data?.find((d) => d.name === ds)?.labels ?? [];
  const list = useApi<GraphPage>(
    `/datasets/${ds}/graphs` +
      query({ label, min_nodes: minNodes, max_nodes: maxNodes, q, sort, page, size: SIZE }),
  );
  const pages = list.data ? Math.max(1, Math.ceil(list.data.total / SIZE)) : 1;

  return (
    <section>
      <header className="page-head">
        <h1>{t("explorer.title")}</h1>
        <p className="muted lead">{t("explorer.lead")}</p>
      </header>

      <div className="toolbar">
        <Segmented
          label={t("explorer.dataset")}
          value={ds}
          options={(["gossipcop", "politifact"] as const).map((d) => ({
            value: d,
            label: datasetText(d, t),
          }))}
          onChange={(v) => update({ ds: v, label: "" })}
        />
        <div className="field">
          <label htmlFor="f-label">{t("explorer.label")}</label>
          <select id="f-label" value={label} onChange={(e) => update({ label: e.target.value })}>
            <option value="">{t("explorer.allLabels")}</option>
            {labels.map((l) => (
              <option key={l} value={l}>
                {labelText(l, t)}
              </option>
            ))}
          </select>
        </div>
        <div className="field field-range">
          <span id="f-nodes">{t("explorer.nodes")}</span>
          <input
            aria-labelledby="f-nodes"
            aria-label={t("explorer.minNodes")}
            type="number"
            min={0}
            inputMode="numeric"
            placeholder={t("explorer.min")}
            value={minNodes}
            onChange={(e) => update({ min: e.target.value })}
          />
          <input
            aria-label={t("explorer.maxNodes")}
            type="number"
            min={0}
            inputMode="numeric"
            placeholder={t("explorer.max")}
            value={maxNodes}
            onChange={(e) => update({ max: e.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="f-sort">{t("explorer.sort")}</label>
          <select id="f-sort" value={sort} onChange={(e) => update({ sort: e.target.value })}>
            {SORTS.map((s) => (
              <option key={s} value={s}>
                {t(`explorer.sorts.${s}`)}
              </option>
            ))}
          </select>
        </div>
        <div className="field field-search">
          <label htmlFor="f-q">{t("explorer.search")}</label>
          <div className="input-icon">
            <Search size={16} aria-hidden="true" />
            <input
              id="f-q"
              type="search"
              value={qDraft}
              placeholder={t("explorer.searchPlaceholder")}
              onChange={(e) => setQDraft(e.target.value)}
            />
          </div>
        </div>
      </div>

      <StateView
        loading={list.loading && !list.data}
        error={list.error}
        onRetry={list.reload}
        empty={list.data?.total === 0}
        emptyText={t("explorer.empty")}
      >
        {list.data && (
          <>
            <p className="muted count" aria-live="polite">
              {t("explorer.count", { count: list.data.total })}
            </p>
            <div className="table-wrap">
              <table className="data graphs">
                <thead>
                  <tr>
                    <th scope="col">{t("explorer.col.gid")}</th>
                    <th scope="col">{t("explorer.col.title")}</th>
                    <th scope="col">{t("explorer.col.label")}</th>
                    <th scope="col" className="num">
                      {t("explorer.col.nodes")}
                    </th>
                    <th scope="col" className="num">
                      {t("explorer.col.depth")}
                    </th>
                    <th scope="col" className="num">
                      {t("explorer.col.span")}
                    </th>
                    <th scope="col">{t("explorer.col.growth")}</th>
                  </tr>
                </thead>
                <tbody>
                  {list.data.items.map((g) => (
                    <tr key={g.gid}>
                      <td className="num">{g.gid}</td>
                      <td className="title-cell">
                        <Link to={`/graphs/${ds}/${g.gid}`}>
                          {g.title || t("explorer.untitled", { id: g.news_id ?? g.gid })}
                        </Link>
                      </td>
                      <td>
                        <span className={`badge badge-${g.label ?? "none"}`}>
                          {labelText(g.label, t)}
                        </span>
                      </td>
                      <td className="num">{formatInt(g.n_nodes, i18n.language)}</td>
                      <td className="num">{g.depth}</td>
                      <td className="num">{formatHours(g.span_h, t, i18n.language)}</td>
                      <td>
                        <Sparkline values={g.growth} label={t("explorer.growthTitle")} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <nav className="pager" aria-label={t("explorer.pager")}>
              <button
                type="button"
                className="btn"
                disabled={page <= 1}
                onClick={() => update({ page: String(page - 1) }, false)}
              >
                <ChevronLeft size={16} aria-hidden="true" />
                {t("explorer.prev")}
              </button>
              <span>{t("explorer.page", { page, pages })}</span>
              <button
                type="button"
                className="btn"
                disabled={page >= pages}
                onClick={() => update({ page: String(page + 1) }, false)}
              >
                {t("explorer.next")}
                <ChevronRight size={16} aria-hidden="true" />
              </button>
            </nav>
          </>
        )}
      </StateView>
    </section>
  );
}
