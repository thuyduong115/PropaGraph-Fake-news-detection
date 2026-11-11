// Thang màu thời gian (log): sớm = đậm/lạnh, muộn = sáng/ấm. Các điểm dừng là biến CSS
// (--t0…--t4) để chế độ tối có bộ màu riêng đủ tương phản.

export const TIME_STOPS_H = [0.1, 1, 10, 100, 1000];

/** Vị trí 0..1 trên thang log của t (giờ). */
export function timePosition(t: number | null): number {
  if (t === null) return 1;
  const lo = Math.log10(TIME_STOPS_H[0]);
  const hi = Math.log10(TIME_STOPS_H[TIME_STOPS_H.length - 1]);
  const v = (Math.log10(Math.max(t, TIME_STOPS_H[0])) - lo) / (hi - lo);
  return Math.min(1, Math.max(0, v));
}

/** Chỉ số điểm dừng gần nhất (0..4): dùng làm class màu, render nhanh hơn nội suy từng node. */
export function timeBucket(t: number | null): number {
  return Math.round(timePosition(t) * (TIME_STOPS_H.length - 1));
}
