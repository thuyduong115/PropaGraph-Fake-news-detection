import type { TFunction } from "i18next";

/** Thời gian lan truyền dạng đọc được: phút / giờ / ngày, theo ngôn ngữ hiện tại. */
export function formatHours(h: number | null | undefined, t: TFunction, lang: string): string {
  if (h === null || h === undefined) return t("time.unknown");
  const nf = (v: number, digits: number) =>
    new Intl.NumberFormat(lang, { maximumFractionDigits: digits }).format(v);
  if (h < 1) return t("time.minutes", { value: nf(h * 60, 0) });
  if (h < 48) return t("time.hours", { value: nf(h, 1) });
  return t("time.days", { value: nf(h / 24, 1) });
}

/** Nhãn mốc thanh trượt: null = toàn bộ cây. */
export function formatCutoff(c: number | null, t: TFunction, lang: string): string {
  return c === null ? t("time.all") : formatHours(c, t, lang);
}

export function formatPercent(p: number, lang: string): string {
  return new Intl.NumberFormat(lang, { style: "percent", maximumFractionDigits: 1 }).format(p);
}

export function formatInt(n: number, lang: string): string {
  return new Intl.NumberFormat(lang).format(n);
}

/** Nhãn hiển thị: dịch "fake"/"real" nếu có trong i18n, ngược lại giữ nguyên giá trị dữ liệu. */
export function labelText(label: string | null, t: TFunction): string {
  if (!label) return t("labels.unknown");
  return t(`labels.${label}`, { defaultValue: label });
}

/** Tên tập dữ liệu hiển thị. */
export function datasetText(ds: string, t: TFunction): string {
  return t(`datasets.${ds}`, { defaultValue: ds });
}
