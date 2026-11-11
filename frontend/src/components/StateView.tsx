import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  loading: boolean;
  error?: Error;
  empty?: boolean;
  emptyText?: string;
  onRetry?: () => void;
  children?: ReactNode;
}

/** Trạng thái chung: đang tải, lỗi (kèm thử lại), rỗng, hoặc nội dung. */
export function StateView({ loading, error, empty, emptyText, onRetry, children }: Props) {
  const { t } = useTranslation();
  if (error) {
    return (
      <div className="state state-error" role="alert">
        <p>{t("common.error", { message: error.message })}</p>
        {onRetry && (
          <button type="button" className="btn" onClick={onRetry}>
            {t("common.retry")}
          </button>
        )}
      </div>
    );
  }
  if (loading) return <p className="state">{t("common.loading")}</p>;
  if (empty) return <p className="state">{emptyText ?? t("common.empty")}</p>;
  return <>{children}</>;
}
