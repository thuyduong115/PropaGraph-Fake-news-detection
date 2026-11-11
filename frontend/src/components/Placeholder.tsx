import { useTranslation } from "react-i18next";

/** Khung tạm cho trang chưa làm; nội dung thật ở P3–P4 (BACKLOG). */
export default function Placeholder({ page, task }: { page: string; task: string }) {
  const { t } = useTranslation();
  return (
    <section>
      <h1>{t(`pages.${page}.title`)}</h1>
      <p className="muted">{t(`pages.${page}.summary`)}</p>
      <p className="note">{t("common.notBuilt", { task })}</p>
    </section>
  );
}
