import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import en from "./en.json";
import vi from "./vi.json";

// Tiếng Việt mặc định; tiếng Anh cho báo cáo/slide (README §5). Mọi chuỗi UI nằm trong JSON.
void i18n.use(initReactI18next).init({
  resources: { vi: { translation: vi }, en: { translation: en } },
  lng: "vi",
  fallbackLng: "vi",
  interpolation: { escapeValue: false },
});

export default i18n;
