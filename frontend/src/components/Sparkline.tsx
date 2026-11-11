/** Mini-sparkline kích thước cây theo các mốc thời gian (README §5, trang Explorer). */
export default function Sparkline({ values, label }: { values: number[]; label: string }) {
  const w = 96;
  const h = 24;
  const max = Math.max(1, ...values);
  const d = values
    .map((v, i) => {
      const x = (i / Math.max(1, values.length - 1)) * (w - 2) + 1;
      const y = h - 2 - (v / max) * (h - 4);
      return `${i ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join("");
  return (
    <svg className="spark" width={w} height={h} viewBox={`0 0 ${w} ${h}`} role="img">
      <title>{label}</title>
      <path d={d} />
    </svg>
  );
}
