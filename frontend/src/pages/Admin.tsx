import { RefreshCw } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { apiPost } from "../api/client";
import type { AdminStatus } from "../api/types";
import { clearApiCache, useApi } from "../api/useApi";
import { StateView } from "../components/StateView";

export default function Admin() {
  const { t, i18n } = useTranslation();
  const status = useApi<AdminStatus>("/admin/status");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const reload = async () => {
    setBusy(true);
    setMessage(null);
    try {
      await apiPost<AdminStatus>("/admin/reload");
      clearApiCache();
      status.reload();
      setMessage(t("admin.reloaded"));
    } catch (err) {
      setMessage(t("common.error", { message: (err as Error).message }));
    } finally {
      setBusy(false);
    }
  };

  const s = status.data;
  return (
    <section>
      <header className="page-head">
        <h1>{t("admin.title")}</h1>
        <p className="muted lead">{t("admin.lead")}</p>
      </header>
      <StateView loading={status.loading && !s} error={status.error} onRetry={status.reload}>
        {s && (
          <>
            <dl className="facts facts-wide">
              <dt>{t("admin.artifactsDir")}</dt>
              <dd className="mono">{s.artifacts_dir}</dd>
              <dt>{t("admin.loadedAt")}</dt>
              <dd>{new Date(s.loaded_at * 1000).toLocaleString(i18n.language)}</dd>
              <dt>{t("admin.synthetic")}</dt>
              <dd>{s.synthetic ? t("common.yes") : t("common.no")}</dd>
              <dt>{t("admin.datasets")}</dt>
              <dd>
                {Object.entries(s.datasets)
                  .map(([k, v]) => `${k}: ${v}`)
                  .join(", ") || t("common.none")}
              </dd>
              <dt>{t("admin.tables")}</dt>
              <dd>{s.tables.join(", ") || t("common.none")}</dd>
              <dt>{t("admin.figures")}</dt>
              <dd>{s.figures}</dd>
              <dt>{t("admin.modelCard")}</dt>
              <dd>{s.model_card ? t("common.yes") : t("common.no")}</dd>
              <dt>{t("admin.models")}</dt>
              <dd>{s.models_loaded.join(", ") || t("common.none")}</dd>
            </dl>
            {s.problems.length > 0 && (
              <div className="state state-error" role="alert">
                <h2>{t("admin.problems")}</h2>
                <ul>
                  {s.problems.map((p) => (
                    <li key={p}>{p}</li>
                  ))}
                </ul>
              </div>
            )}
            {s.notes.length > 0 && (
              <div className="note">
                <h2>{t("admin.notes")}</h2>
                <ul>
                  {s.notes.map((p) => (
                    <li key={p}>{p}</li>
                  ))}
                </ul>
              </div>
            )}
            <button type="button" className="btn btn-primary" disabled={busy} onClick={reload}>
              <RefreshCw size={16} aria-hidden="true" />
              {busy ? t("admin.reloading") : t("admin.reload")}
            </button>
            {message && (
              <p role="status" className="muted">
                {message}
              </p>
            )}
          </>
        )}
      </StateView>
    </section>
  );
}
