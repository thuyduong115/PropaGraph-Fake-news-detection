import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import en from "./en.json";
import vi from "./vi.json";

function savedLanguage(): string {
  try {
    const lang = localStorage.getItem("lang");
    if (lang === "vi" || lang === "en") return lang;
  } catch {
    /* localStorage bị chặn */
  }
  return "vi";
}

// Tiếng Việt mặc định; tiếng Anh cho báo cáo/slide (docs/development.md §5). Mọi chuỗi UI nằm trong JSON.
void i18n.use(initReactI18next).init({
  resources: { vi: { translation: vi }, en: { translation: en } },
  lng: savedLanguage(),
  fallbackLng: "vi",
  interpolation: { escapeValue: false },
});

export default i18n;
