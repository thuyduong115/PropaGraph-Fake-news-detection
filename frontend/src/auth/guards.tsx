import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "./AuthContext";

/** Chỉ ẩn trang; quyền thật kiểm tra ở backend. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { me, checking } = useAuth();
  const location = useLocation();
  const { t } = useTranslation();
  if (checking) return <p className="state">{t("common.loading")}</p>;
  if (!me) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <>{children}</>;
}

export function RequireAdmin({ children }: { children: ReactNode }) {
  const { me } = useAuth();
  const { t } = useTranslation();
  if (me?.role !== "admin") return <p className="state">{t("admin.forbidden")}</p>;
  return <>{children}</>;
}
