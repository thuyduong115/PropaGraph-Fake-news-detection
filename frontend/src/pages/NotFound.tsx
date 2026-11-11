import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

export default function NotFound() {
  const { t } = useTranslation();
  return (
    <section>
      <h1>{t("pages.notFound.title")}</h1>
      <Link to="/">{t("pages.notFound.back")}</Link>
    </section>
  );
}
