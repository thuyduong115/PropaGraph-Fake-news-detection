import { Languages, LogOut, Moon, Sun, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import type { Health } from "../api/types";
import { useApi } from "../api/useApi";
import { useAuth } from "../auth/AuthContext";

type Theme = "light" | "dark";

function initialTheme(): Theme {
  try {
    const saved = localStorage.getItem("theme");
    if (saved === "light" || saved === "dark") return saved;
  } catch {
    /* localStorage bị chặn: dùng theo hệ thống */
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function Layout() {
  const { t, i18n } = useTranslation();
  const { me, logout } = useAuth();
  const navigate = useNavigate();
  const [theme, setTheme] = useState<Theme>(initialTheme);
  const health = useApi<Health>("/health");

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("theme", theme);
    } catch {
      /* bỏ qua */
    }
  }, [theme]);

  useEffect(() => {
    document.documentElement.lang = i18n.language;
    try {
      localStorage.setItem("lang", i18n.language);
    } catch {
      /* bỏ qua */
    }
  }, [i18n.language]);

  const signedIn = me && me.username !== "anonymous";
  const nav = [
    { to: "/", key: "nav.explorer", end: true },
    { to: "/results", key: "nav.results" },
    { to: "/data-reliability", key: "nav.dataReliability" },
    { to: "/about", key: "nav.about" },
    ...(me?.role === "admin" ? [{ to: "/admin", key: "nav.admin" }] : []),
  ];

  return (
    <div className="shell">
      <a href="#main" className="skip">
        {t("nav.skip")}
      </a>
      <header className="header">
        <NavLink to="/" className="brand">
          <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="4" className="brand-root" />
            <circle cx="4" cy="5" r="2" className="brand-leaf" />
            <circle cx="20" cy="6" r="2" className="brand-leaf" />
            <circle cx="6" cy="20" r="2" className="brand-leaf" />
            <path d="M12 12 4 5M12 12l8-6M12 12l-6 8" className="brand-edge" />
          </svg>
          {t("app.name")}
        </NavLink>
        {me && (
          <nav className="nav" aria-label={t("nav.label")}>
            {nav.map((item) => (
              <NavLink key={item.to} to={item.to} end={item.end}>
                {t(item.key)}
              </NavLink>
            ))}
          </nav>
        )}
        <div className="tools">
          <button
            type="button"
            className="icon-btn"
            onClick={() => i18n.changeLanguage(i18n.language === "vi" ? "en" : "vi")}
            aria-label={t("tools.languageAria")}
            title={t("tools.languageAria")}
          >
            <Languages size={18} aria-hidden="true" />
            <span>{t("tools.language")}</span>
          </button>
          <button
            type="button"
            className="icon-btn"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            aria-label={theme === "dark" ? t("tools.lightMode") : t("tools.darkMode")}
            title={theme === "dark" ? t("tools.lightMode") : t("tools.darkMode")}
          >
            {theme === "dark" ? (
              <Sun size={18} aria-hidden="true" />
            ) : (
              <Moon size={18} aria-hidden="true" />
            )}
          </button>
          {signedIn && (
            <button
              type="button"
              className="icon-btn"
              onClick={async () => {
                await logout();
                navigate("/login");
              }}
              title={t("tools.logout")}
            >
              <LogOut size={18} aria-hidden="true" />
              <span>
                {me.username} ({t(`roles.${me.role}`)})
              </span>
            </button>
          )}
        </div>
      </header>
      {health.data?.synthetic && (
        <div className="banner" role="note">
          <TriangleAlert size={18} aria-hidden="true" />
          {t("banner.synthetic")}
        </div>
      )}
      <main id="main" className="main">
        <Outlet />
      </main>
      <footer className="footer">
        <p>{t("footer.disclaimer")}</p>
      </footer>
    </div>
  );
}
