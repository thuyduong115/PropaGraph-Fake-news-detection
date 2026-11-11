// Bảng pivot pandas (cột nhiều tầng) khi ghi CSV có dạng:
//   dataset,gossipcop,gossipcop,…   ← dòng tiêu đề tầng 1 (thành `columns`)
//   feature,bert,content,…          ← tầng 2 (rows[0])
//   model,,,…                       ← tên chỉ mục, các ô còn lại trống
//   GAT,0.963 ± 0.002,…             ← dữ liệu
// Hàm này chỉ tách lại phần tiêu đề để hiển thị; không đổi giá trị ô nào (AGENTS.md quy tắc 2).

export interface HeaderCell {
  text: string;
  span: number;
}

export interface ShapedTable {
  header: HeaderCell[][];
  body: string[][];
}

const MAX_LEVELS = 4;

/** Vị trí dòng tên chỉ mục (ô đầu có chữ, còn lại trống), hoặc -1 nếu không phải bảng pivot. */
function indexNameRow(rows: string[][]): number {
  for (let k = 0; k < Math.min(rows.length, MAX_LEVELS); k++) {
    const r = rows[k];
    if (!r[0]) return -1;
    if (r.length > 1 && r.slice(1).every((c) => c === "")) return k;
  }
  return -1;
}

/** Gộp các ô liền nhau giống nhau thành một ô colSpan (chỉ khi các tầng trên cũng giống). */
function merge(level: string[], above: HeaderCell[] | null): HeaderCell[] {
  const bounds = new Set<number>();
  if (above) {
    let pos = 0;
    for (const c of above) bounds.add((pos += c.span));
  }
  const out: HeaderCell[] = [];
  level.forEach((text, i) => {
    const last = out[out.length - 1];
    if (i > 0 && last && last.text === text && !bounds.has(i)) last.span += 1;
    else out.push({ text, span: 1 });
  });
  return out;
}

export function shapeTable(columns: string[], rows: string[][]): ShapedTable {
  const k = indexNameRow(rows);
  if (k < 0) {
    return { header: [columns.map((text) => ({ text, span: 1 }))], body: rows };
  }
  const levels = [columns, ...rows.slice(0, k)];
  const indexName = rows[k][0];
  const header: HeaderCell[][] = [];
  levels.forEach((lv, li) => {
    const label = li === levels.length - 1 ? `${lv[0]} / ${indexName}` : lv[0];
    const merged = merge(lv.slice(1), li > 0 ? header[li - 1].slice(1) : null);
    header.push([{ text: label, span: 1 }, ...merged]);
  });
  return { header, body: rows.slice(k + 1) };
}
