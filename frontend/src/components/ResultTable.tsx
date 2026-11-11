import { useMemo } from "react";
import { useTranslation } from "react-i18next";

import type { TableData } from "../api/types";
import { useApi } from "../api/useApi";
import { shapeTable } from "../lib/tables";
import { StateView } from "./StateView";

/** Bảng CSV hiển thị nguyên văn như notebook xuất (không làm tròn, không tính lại).
 *  Bảng pivot nhiều tầng tiêu đề được dựng lại phần thead (`lib/tables.ts`). */
export default function ResultTable({ name, notes }: { name: string; notes: string[] }) {
  const { t } = useTranslation();
  const { data, error, loading, reload } = useApi<TableData>(
    `/results/tables/${encodeURIComponent(name)}`,
  );
  const shaped = useMemo(() => (data ? shapeTable(data.columns, data.rows) : null), [data]);

  return (
    <section className="result-block" aria-labelledby={`tbl-${name}`}>
      <h2 id={`tbl-${name}`}>{name}</h2>
      {notes.length > 0 ? (
        notes.map((p, i) => <p key={i}>{p}</p>)
      ) : (
        <p className="muted">{t("results.noInterpretation")}</p>
      )}
      <StateView loading={loading} error={error} onRetry={reload}>
        {shaped && (
          <div className="table-wrap">
            <table className="data">
              <thead>
                {shaped.header.map((level, li) => (
                  <tr key={li}>
                    {level.map((c, j) => (
                      <th key={j} scope={c.span > 1 ? "colgroup" : "col"} colSpan={c.span}>
                        {c.text}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {shaped.body.map((row, i) => (
                  <tr key={i}>
                    {row.map((cell, j) => (
                      <td key={j}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </StateView>
    </section>
  );
}
