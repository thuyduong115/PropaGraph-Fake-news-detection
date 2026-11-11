import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { NavLink, Outlet } from "react-router-dom";

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

const NAV = [
  { to: "/", key: "nav.explorer", end: true },
  { to: "/results", key: "nav.results" },
  { to: "/data-reliability", key: "nav.dataReliability" },
  { to: "/about", key: "nav.about" },
];

export default function Layout() {
  const { t, i18n } = useTranslation();
  const [theme, setTheme] = useState<Theme>(initialTheme);

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
  }, [i18n.language]);

  const nextLang = i18n.language === "vi" ? "en" : "vi";

  return (
    <div className="shell">
      <header className="header">
        <NavLink to="/" className="brand">
          {t("app.name")}
        </NavLink>
        <nav className="nav" aria-label={t("nav.label")}>
          {NAV.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end}>
              {t(item.key)}
            </NavLink>
          ))}
        </nav>
        <div className="tools">
          <button type="button" onClick={() => i18n.changeLanguage(nextLang)}>
            {t("tools.language")}
          </button>
          <button type="button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
            {theme === "dark" ? t("tools.lightMode") : t("tools.darkMode")}
          </button>
        </div>
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="footer">
        <p>{t("footer.disclaimer")}</p>
      </footer>
    </div>
  );
}
