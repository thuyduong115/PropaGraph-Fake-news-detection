import { useTranslation } from "react-i18next";

import type { TableData } from "../api/types";
import { useApi } from "../api/useApi";
import { StateView } from "./StateView";

/** Bảng CSV hiển thị nguyên văn như notebook xuất (không làm tròn, không tính lại). */
export default function ResultTable({ name, notes }: { name: string; notes: string[] }) {
  const { t } = useTranslation();
  const { data, error, loading, reload } = useApi<TableData>(
    `/results/tables/${encodeURIComponent(name)}`,
  );

  return (
    <section className="result-block" aria-labelledby={`tbl-${name}`}>
      <h2 id={`tbl-${name}`}>{name}</h2>
      {notes.length > 0 ? (
        notes.map((p, i) => <p key={i}>{p}</p>)
      ) : (
        <p className="muted">{t("results.noInterpretation")}</p>
      )}
      <StateView loading={loading} error={error} onRetry={reload}>
        {data && (
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  {data.columns.map((c) => (
                    <th key={c} scope="col">
                      {c}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.rows.map((row, i) => (
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
